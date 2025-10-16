

from fastapi import APIRouter, HTTPException, Depends, Response, Request, Body, Path, UploadFile, File, status, Query, Form, WebSocket, WebSocketDisconnect
from typing import Any
import random
import asyncio
# from bson import ObjectId
from datetime import datetime, timezone
from beanie import PydanticObjectId
from bson import DBRef
import json
import uuid
from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse
from beanie import Link
from bson import ObjectId, DBRef
from beanie import SortDirection
import math

# my imports
from src.models import User, Otp, Upload, PDF, PdfPage
from src.services import fire_task
from src.dtos import TaskTypes, Dictor, UploadStatus
from src.services import send_email, generate_jwt, verify_jwt, verify_token
from src.config import settings
from src.dependencies import auth_guard, guest_guard
from src.langchain import delete_pdf_vectors

# schemas
from src.schemas import RegisterInput, LoginInput, ProfileResponse, UserCreate, MeResponse

# routers 
user_router = APIRouter(prefix='/users', tags=['users'])
pdf_router = APIRouter(prefix='/pdfs', tags=['pdfs'])
sse_router = APIRouter(prefix='/sse', tags=['sse'])

#==============
# User routes
#==============

# register methods
#=================

async def get_or_create_user(email: str) -> User:
  """ get user by email and create if does not exists """
  user = await User.find_one({"email": email}) # beanie

  if not user:
    # create a new user if does not exist
    user = User(email=email)
    await user.insert()

  return user

async def create_otp(payload: Dictor) -> Otp:
  """ generate otp_code & create an Otp record """

  # 6-digits code
  otp_code = str(random.randint(10000, 999999))

  otp_record = Otp(
    otp_code=otp_code,
    user=payload['user'],
  ) 

  await otp_record.insert()

  return otp_record

# /users/register
@user_router.post(path="/register", dependencies=[Depends(guest_guard)])
async def register(
  data: RegisterInput,
):
  # data
  email = data.email

  # create a user if does not exist
  user = await get_or_create_user(email=email)

  # generate otp code and store a record inside of db
  otp_record = await create_otp(payload={"user": user})

  # send email
  print(f"sending email: {user.email} - {otp_record.otp_code}")

  # send an email
  # asyncio.create_task(send_email(
  #   to_email=user.email,
  #   subject="Your OTP code", 
  #   body=f"hi, your otp code is : {otp_record.otp_code}"
  # ))

  return {"message": "register success", "otp_code": otp_record.otp_code}

# ============= methods

async def check_user_exists(email: str) -> User:
  """ get user by email, return if exists """

  user = await User.find_one({"email": email})

  if not user:
    raise HTTPException(status_code=404, detail="User not found")

  return user

async def verify_otp(user: User, otp_code: str) -> Otp:
  """ get otp record & raise exception is does not exists """

  otp : Otp | None = await Otp.find_one(
    dict(user=DBRef(collection='users', id=user.id), otp_code=otp_code),
  )

  print(user.id, otp_code, "\n")
  print(otp)
  # check if current user has such otp
  if not otp:
    raise HTTPException(status_code=400, detail="invalid otp")

  return otp

def check_otp_expiration(expires_at: datetime) -> None:
  """ check otp expiration date, also: add timezone to db field """

  # force db field to include timezone
  if expires_at.tzinfo is None:
    expires_at = expires_at.replace(tzinfo=timezone.utc)

  # check is otp is expired
  print(expires_at, datetime.now(timezone.utc))
  if expires_at < datetime.now(timezone.utc):
    raise HTTPException(status_code=400, detail="OTP expired")

def generate_jwt_set_cookie(payload: Dictor, response: Response):
  """ generate jwt and set it in http only cookie """

  access_token = generate_jwt(payload=payload)

  # set access-token in http only cookie
  # localhost:8000
  # localhost:5000
  response.set_cookie(
    key="access_token", # name of cookie
    value=access_token,
    httponly=True,
    samesite='lax',
    #samesite='none', # secure must be True -> only works over https
    max_age=settings.JWT_EXPIRE_MINS,
    secure=False,
    # secure=
    # domain=
  )

@user_router.post(path="/login", dependencies=[Depends(guest_guard)])
async def login(
  response: Response,
  data: LoginInput = Body(...),
):
  # data
  email = data.email
  otp_code = data.otp_code

  user = await check_user_exists(email=email)

  # verify otp
  otp = await verify_otp(user=user, otp_code=otp_code)

  check_otp_expiration(expires_at=otp.expires_at)

  # delete otp
  await otp.delete()

  # jwt payload
  payload = dict(user_id= str(user.id), email=user.email)

  generate_jwt_set_cookie(payload=payload, response=response)

  return dict(message="login success", user=user.model_dump(mode="json"))

  

@user_router.post(path="/logout")
async def logout(response: Response):
  
  # remove jwt from cookie
  response.delete_cookie(key='access_token')

  return dict(message="logged out success")
  

@user_router.get(path="/profile", response_model=ProfileResponse)
async def profile(
  auth_user: User = Depends(dependency=auth_guard)
):
  print("profile request: ", auth_user.email)
  return dict(email=auth_user.email, plan=auth_user.plan)

@user_router.post(path="/me", response_model=MeResponse)
async def me(request: Request):
  
  # check if token exists and valid
  payload: Dictor | None = verify_token(request=request)

  if not payload: 
    return MeResponse(authenticated=False)
  
  user_id = payload.get("user_id")

  user = await User.get(document_id=PydanticObjectId(oid=user_id))

  if not user:
    return MeResponse(authenticated=False)

  # valid authenticated user
  return MeResponse(
    authenticated=True,
    user=user
  )

@user_router.get(path='')
async def get_users() -> Any:

  

  users = await User.find_all().to_list()
  return users

@user_router.post(path="")
async def create_user(
  user_in: UserCreate = Body(...),
) -> Any:
  # input data
  email = user_in.email
  name = user_in.name

  # create a new user
  user = User(email=email, name=name)

  # insert into mongo
  await user.insert()

  return {
    "message": 'user created',
    "user": user
  }

#==============
# PDF upload routes
#==============
  
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
from src.services import compute_file_hash
from src.dtos import UploadEvents, PDFStatus

# upload pdf route
@pdf_router.post("/upload-pdf")# 
async def upload_pdf(
  background_tasks: BackgroundTasks, # fastapi injects this 
  request: Request,
  # data: Any = Body(...),
  file: UploadFile = File(...),
  #upload_id: str = Form(...),
  file_size: int = Form(...),
  auth_user: User = Depends(dependency=auth_guard),
):
  """
  upload pdf chunk by chunk and increment upload process
  """

  # data
  # file 
  # upload_id
  # auth_user

  # db instance
  db: AsyncIOMotorDatabase[Any] = request.app.state.mongo_db
  # grid bucket
  bucket = AsyncIOMotorGridFSBucket(database=db)

  # hash our file
  file_hash = await compute_file_hash(file=file)

  # existing upload 
  existing_upload = await Upload.find_one(
    dict(
      user=DBRef(collection='users', id=auth_user.id),
      file_hash=file_hash,
      status=UploadStatus.UPLOADING,
    )
  )

  if existing_upload:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="upload already in progress for this file")
  
  # init upload if does not exists
  upload_doc = Upload(
    user=auth_user, # type: ignore
    filename=file.filename,
    file_size=file.spool_max_size if hasattr(file, "spool_max_size") else file_size, #type: ignore
    file_hash=file_hash,
    status=UploadStatus.UPLOADING,
    percent=0,
  )
  await upload_doc.insert()

  # background task: upload
  async def upload_chunks(
      file: UploadFile,
      # upload_id: str ,
      upload_record: Upload,
      user: User,
  ):
    try:
      # open GridFs upload stream
      grid_in = bucket.open_upload_stream(filename=file.filename) # type: ignore

      chunk_size = 1024 * 1024 # 1 mb -> in each upload loop
      total_bytes = 0 # track uploaded chunks

      while True:
        # read a chunk
        chunk = await file.read(chunk_size)
        
        if not chunk:
          break # not chunk left

        # write to gridfs
        await grid_in.write(data=chunk)

        # increment total chunk read
        total_bytes += len(chunk) # number of bytes

        # calculate upload.percent
        percent = math.floor((total_bytes / upload_record.file_size) * 100)

        # update upload doc
        #upload_record = await Upload.find_one(Upload.upload_id == upload_id)
        # increase upload progress
        upload_record.percent = min(percent, 100) # type: ignore

        await upload_record.save() # type: ignore

        # send an event to frontend
        await event_manager.publish(
          user_id=str(user.id),
          event=UploadEvents.UPLOAD_PROGRESS.value,
          data=upload_record.model_dump(mode="json"), # type: ignore
        )

        # some delay
        await asyncio.sleep(1)

      # close bucket
      await grid_in.close()

      # mark upload as done
      #upload_doc: Any = await Upload.find_one(Upload.upload_id == upload_id)
      upload_record.status = UploadStatus.DONE
      upload_record.file_id =str(grid_in._id)
      upload_record.percent = 100
      await upload_record.save()

      # create a PDF doc -> metadata, text, html
      pdf_doc = PDF(
        filename=file.filename, # type: ignore
        gridfs_id=str(grid_in._id),
        upload_id= str(upload_record.id),
        user=user, # type: ignore
        status=PDFStatus.UPLOADED,
      )
      
      await pdf_doc.insert()

      # event: upload complete
      await event_manager.publish(
        user_id=str(user.id),
        event=UploadEvents.UPLOAD_DONE.value,
        data=upload_record.model_dump(mode="json"), # type:ignore
      )

      # pdf upload success -> init pdf extraction process (task)
      await fire_task(
        task_type=TaskTypes.PROCESSING,
        payload=dict(pdf_id=pdf_doc.id, user_id=auth_user.id)
      )

    except Exception as e:
      print(str(e))
      # pdf upload failed
      #upload_record = await Upload.find_one(Upload.upload_id == upload_id)
      upload_record.status = UploadStatus.FAILED # upload failed
      upload_record.error = str(e)
      await upload_record.save()

      # event: upload failed
      await event_manager.publish(
        user_id=str(user.id),
        event=UploadEvents.UPLOAD_FAILED,
        data=upload_doc.model_dump(mode="json")
      )


  # background task
  background_tasks.add_task(
    upload_chunks, # async process /function
    file,
    upload_record=upload_doc,
    user=auth_user
  )

  return dict(message="✅ pdf upload in progress.")


# route /pdfs/my-pdfs
@pdf_router.get("/my-pdfs", response_model=list[PDF])
async def get_user_pdfs(
  auth_user: User = Depends(dependency=auth_guard),
):
  """ return all pdfs belonging to the auth user """
  # dict(user=DBRef(collection='users', id=user.id)

  pdfs = await PDF.find(dict(user=DBRef(collection='users', id=auth_user.id))).sort([("created_at", SortDirection.DESCENDING)]).to_list()
  
  return pdfs

# download
@pdf_router.get("/download/{pdf_id}") # gridFS
async def download_pdf(
  request: Request,
  pdf_id: str = Path(..., description="PDF file ID"),
  auth_user: User = Depends(auth_guard),
):
  # data:
  # pdf_id
  # auth_user.id
  # request.app.state.mongo_db

  """ download a stored file from GridFS """
  mongo = request.app.state.mongo_db
  bucket = AsyncIOMotorGridFSBucket(database=mongo)

  # find a PDF by user and pdf_id
  pdf_doc = await PDF.find_one(dict(
    user=DBRef(collection='users', id=auth_user.id),
    _id=ObjectId(pdf_id), # underscore & ObjectId
  ))
  
  if not pdf_doc:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="file not found or access denied")

  try:
    # gridFS file id
    file_id = ObjectId(pdf_doc.gridfs_id)

    # open download stream
    stream = await bucket.open_download_stream(file_id=file_id)

    # filename and content_type -> for setting the headers

    filename = stream._file.get("filename", "download.pdf")
    content_type = stream._file.get("contentType", "application/pdf")

    # response back to the client
    return StreamingResponse(
      stream,
      media_type=content_type,
      headers={
        # Content-Disposition: inline -> for opening a tab
        "Content-Disposition": f'attachment; filename="{filename}"'
      }
    )

  except Exception as e:
    # download failed
    print("GridFS download failed: ", str(e))
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="file not found")

# delete
@pdf_router.delete("/{pdf_id}")
async def delete_pdf(
  request: Request,
  pdf_id: str = Path(...),
  auth_user: User = Depends(auth_guard),
  ): 
  """ given a pdf_id -> remove everything related to PDF on our backend """

  db: AsyncIOMotorDatabase[Any] = request.app.state.mongo_db
  # grid bucket
  bucket = AsyncIOMotorGridFSBucket(database=db)

  if not ObjectId.is_valid(oid=pdf_id):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PDF ID")

  pdf_doc = await PDF.get(document_id=pdf_id)

  if not pdf_doc:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not found")

  print(f"deleting PDF {pdf_id}")

  # delete all PdfPage docs
  # dict(pdf=DBRef(collection="PDF", id=ObjectId(oid=pdf_id)))
  # result: Any = await PdfPage.find_many(PdfPage.pdf == ObjectId(pdf_id)).delete_many()

  # make the DBRef object to match
  pdf_ref = DBRef(collection="pdfs", id=ObjectId(pdf_id))

  # delete all pages linked to this PDF
  result = await PdfPage.find({'pdf': pdf_ref}).delete()

  print(f"deleted {result.deleted_count} pages") # type: ignore

  # delete the file from GridFS
  file_id: Any = pdf_doc.gridfs_id # type: ignore

  if file_id:
    try:
      file_oid = ObjectId(file_id) # type: ignore
      await bucket.delete(file_id=file_oid)
      print(f"deleted file from gridFS: {file_oid}")
    except Exception as e:
      print(f"gridFS delete file error: {str(e)}")
      raise HTTPException(status_code=500, detail=f"Failed to delete GridFS file: {str(e)}")

  # delete all vectors in chroma db
  try:
    delete_pdf_vectors(collection_name='pdf_chunks', pdf_id=pdf_id)
  except Exception as e:
    print(f"failed to delete vectors: {str(e)}")

  # delete PDF doc
  #await PDF.delete(dict(id=pdf_id))
  await pdf_doc.delete()
  print(f"deleted PDF doc: {pdf_id}")

  return dict(status="ok", pdf_id=pdf_id)

#==============
# SSE routes
#==============
from src.events import event_manager
from src.dependencies import websocket_auth_guard
#from typing import AsyncGenerator
#from src.services import format_sse

@sse_router.websocket("/ws")
async def sse_endpoint(
  # request: Request,
  websocket: WebSocket,
  auth_user: Any = Depends(websocket_auth_guard),
):
  """
  single websocket connection per auth user
  """

  user_id = str(auth_user.id)

  # accept a socket connection
  await websocket.accept()
  print(f"{user_id} - connected via socket")

  # subscribe user client ->and return the queue
  queue = await event_manager.subscribe(user_id=user_id)

  try:
   
    while True:

      try:
        # either send event message or send a heartbeat on timeout
        text = await asyncio.wait_for(
          queue.get(), # await a message inside our queue
          timeout=15,
        ) 

        #get data out of our event
        payload = json.loads(text)

        print("data out of our event: 🍹", payload)

        event_name = payload.get("event")
        data = json.dumps(payload.get('data'))

        # socket , send json
        await websocket.send_json(dict(
          event= event_name,
          data= data,
        ))

      except asyncio.TimeoutError:
        # send a heartbeat -> on timeout
        await websocket.send_json(dict(event="ping"))

  except WebSocketDisconnect:
    print(f"🛑 {user_id} disconnected") # on shut down -> generator process get's cancelled

  finally:
    # connection is closed -> so unsub the user
    await event_manager.unsubscribe(user_id=user_id, q=queue)

from datetime import datetime, timezone

# test sse route
@sse_router.post("/sse/test")
async def sse_test(
  auth_user: Any = Depends(auth_guard),
):
  """ test: publish and event that goes to auth user """

  user_id = str(auth_user.id)

  payload = dict(msg="hello from my server", ts=datetime.now(timezone.utc).isoformat())

  await event_manager.publish(
    user_id=user_id,
    event="test_event",
    data=payload,
  )

  return dict(ok= True)