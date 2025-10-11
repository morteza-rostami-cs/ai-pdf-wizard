from email.message import EmailMessage
import aiosmtplib
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status, Request
import fitz
from motor.motor_asyncio import AsyncIOMotorGridFSBucket, AsyncIOMotorDatabase
from typing import Any
from fitz import Document, Page
from dataclasses import asdict
from beanie import PydanticObjectId

from bson import ObjectId, DBRef
from beanie import SortDirection

# my imports 
from src.dtos import TaskTypes, Dictor, PDFStatus
from src.models import Task, PDF, PdfPage, User
from src.config import settings
from src.schemas import PageMetadata
from src.langchain import chunk_pdf_for_embed, create_embedding, store_in_chroma

# fire tasks 
async def fire_task(
    task_type: TaskTypes,
    payload: Dictor,
) -> Task:
  """ 
  store a task in mongodb
  args: task_type and payload data 
  """

  task = Task(
    task_type= task_type,
    payload=payload
  )

  await task.insert()

  print(f"✅ new task {task_type} fired.")

  return task

# send email (smtp gmail)

async def send_email(
    to_email: str,  # receiver
    subject: str, # email subject
    body: str, # email content
):

  smtp_email = settings.SMTP_FROM
  smtp_port = settings.SMTP_PORT
  smtp_host = settings.SMTP_HOST # name of service or my_gmail
  smtp_password = settings.SMTP_PASS
  
  # email message template
  message = EmailMessage()

  message['From'] = smtp_email
  # user email
  message["To"] = to_email
  message['subject'] = subject
  # email  content
  message.set_content(body) 

  # send the email
  await aiosmtplib.send(
    message,
    hostname=smtp_host,
    port=smtp_port,
    start_tls=True,
    username=smtp_email, # my_gmail
    password=smtp_password,
  )

  print(f"email send to: {to_email}")


# generate jwt
def generate_jwt(
    payload: Dictor,
    expires_minutes: int = settings.JWT_EXPIRE_MINS,
):
  """ create jwt token with expiration date """

  # set expiration date
  expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

  # add expiration date to payload
  payload.update({"exp": expire})

  # generate jwt token
  token = jwt.encode(
    claims=payload,
    key=settings.JWT_SECRET_KEY , # jwt secret
    algorithm=settings.JWT_ALGORITHM,
  )

  return token

# verify jwt

def verify_jwt(token: str) -> Dictor:
  """
  verify jwt and return decoded token
  raise 401 -> if invalid or expired
  """

  try:
    decoded = jwt.decode(
      token=token, 
      key=settings.JWT_SECRET_KEY,
      algorithms=[settings.JWT_ALGORITHM],
    )

    return decoded

  except JWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
  

# can verify token
def verify_token(request: Request) -> Dictor | None:
  """ takes request, validate token """

  token = request.cookies.get("access_token")

  if not token:
    print("no token")
    return None
  
  payload = verify_jwt(token=token)

  if not payload:
    print('no payload')
    return None
  
  return payload

# ================================= pdf extraction service

async def extract_text_service(
    db: AsyncIOMotorDatabase[Any],
    #pdf_id: str # PDF
    pdf_doc: PDF,
    user_doc: User,
):
  """
  extract text and html from a PDF stored in gridFS, 
  and store -> per page and full-text
  """

  # set PDF status -> processing
  await pdf_doc.set_status(new_status=PDFStatus.PROCESSING)

  # open file from GridFS
  bucket = AsyncIOMotorGridFSBucket(database=db)
  # open stream
  grid_out = await bucket.open_download_stream(ObjectId(oid=pdf_doc.gridfs_id))
  # read
  pdf_bytes = await grid_out.read()

  # open with pymupdf
  doc: Document = fitz.open(stream=pdf_bytes, filetype='pdf')

  pages: list[PdfPage] = []
  # number of ocr needed pages
  ocr_pages = 0

  for i, page in enumerate(doc):
    page: Page
    # get the text 
    text = page.get_text("text").strip()

    # check
    if not text:
      # mark page as needing OCR
      html = f"""
      <div class="p-6 text-center text-gray-500 bg-gray-100 rounded-lg">
        <p> page {i+1} - image-based, OCR required. </p>
      </div>
      """

      need_ocr = True
      ocr_pages += 1
    else:
      # it is selectable 
      html = f"""
      <article>
        <h2 class="text-lg font-semibold mb-2">Page {i + 1}</h2>
        <pre class="whitespace-pre-wrap text-sm text-gray-800">{text}</pre>
      </article>
      """
      need_ocr = False

    # store page in db
    pdf_page = PdfPage(
      pdf = pdf_doc,
      page_number = i + 1,
      text=text, 
      html=html,
      snippet=text[:200],
      need_ocr=need_ocr,

      user=user_doc,
    )

    await pdf_page.insert()
    # keep all pdf_page docs
    pages.append(pdf_page)

  # update PDT metadata
  await pdf_doc.update({
    "$set": {
      "num_pages": len(pages), 
      "text_content": "\n".join(p.text for p in pages if not p.need_ocr),
      "html_content": "\n".join(p.html for p in pages),
      "status": PDFStatus.NEED_OCR if ocr_pages else PDFStatus.EMBEDDING,
      "updated_at": datetime.now(timezone.utc),
    }
  })
  
  print(f"✅ text extraction service success.")
  # return
  return dict(
    pages_extracted= len(pages),
    ocr_pages=ocr_pages,
    pdf_id=str(pdf_doc.id)
  )


# ================================= prepare pages for embedding

async def prepare_page_for_embedding(
    pdf_id: str # PDF
) -> list[dict[str, Any]]:
  """
  prepares text + metadata per PDF page for embedding.
  skip if PDF requires OCR.
  """

  # fetch PDF doc
  pdf_doc = await PDF.get(document_id=ObjectId(pdf_id))

  if not pdf_doc:
    raise ValueError(f"PDF {pdf_id} not found")

  # check for ocr
  if pdf_doc.status == PDFStatus.NEED_OCR:
    print(f"skipping PDF {pdf_id}: OCR required")
    return []

  # based on PDF, fetch all PdfPage's
  #pages = await PdfPage.find_many(dict(pdf_id=ObjectId(pdf_id))).sort("+page_number").to_list()

  # pages = await PdfPage.find_many(
  #   dict(pdf=DBRef(collection='pdfs', id=pdf_id))
  # ).sort([("page_number", SortDirection.ASCENDING)]).to_list()

  pages = await PdfPage.find_many(PdfPage.pdf.id == PydanticObjectId(pdf_id)).sort("+page_number").to_list() # type: ignore

  # check for pages
  total_pages = len(pages)
  if not total_pages:
    print(f"no pages found for PDF {pdf_id}")
    return []

  # build list for embedding
  docs_to_embed: list[Any] = []

  # user on pdf_doc
  user = await pdf_doc.user.fetch()

  if not user:
    print('can not fetch user')
    return []

  for page in pages:
    meta = PageMetadata(
      pdf_id=str(pdf_id),
      user_id=str(user.id), # type: ignore
      page_number=str(page.page_number),
      total_pages=str(total_pages),
      filename=pdf_doc.filename,
      uploaded_at=pdf_doc.created_at.isoformat(),
    )

    docs_to_embed.append(dict(
      text=page.text, # type: ignore
      metadata=asdict(meta)
    ))

  return docs_to_embed



# ================================= pdf embedding service

async def embedding_service(pdf_id: str):

  # fetch and ready data to vectorize
  data = await prepare_page_for_embedding(pdf_id=pdf_id)

  # chunk our data
  chunks = chunk_pdf_for_embed(
    pages_data=data,
  )

  # vectorize
  results = await create_embedding(
    chunks=chunks,
  )

  store_in_chroma(
    collection_name="pdf_chunks",
    embedding_data=results,
  )

  return results


# sse event strings formatter
def format_sse(
    message_id: int | None,
    event_name: str | None,
    data: str, # json string
) -> str:
  """ return  a properly formatted SSE event string """
  event_str = ""

  if message_id is not None:
    event_str += f"id: {message_id}\n"

  if event_name:
    event_str += f"event: {event_name}\n"

  # sse data \n
  for line in data.splitlines(): # [line1, line2]
    event_str += f"data: {line}\n"

  # \n\n
  event_str += '\n'

  return event_str

from fastapi import UploadFile
import hashlib

# file hash
async def compute_file_hash(file: UploadFile) -> str:
  """ compute a hash of the file for duplicate detection """

  hasher = hashlib.sha256()
  chunk_size = 1024 * 1024 # 1 mb

  while True:
    chunk = await file.read(chunk_size)

    if not chunk:
      break
      
    hasher.update(chunk)
  
  await file.seek(0) # resetting file pointer
  
  return hasher.hexdigest()
