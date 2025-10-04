

from fastapi import APIRouter, HTTPException, Depends, Response, Request, Body, Path, UploadFile, File, status, Query, Form
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
import math

# my imports
from src.models import User, Otp, Upload, PDF
from src.services import fire_task
from src.dtos import TaskTypes, Dictor, UploadStatus
from src.services import send_email, generate_jwt, verify_jwt, verify_token
from src.config import settings
from src.dependencies import auth_guard, guest_guard

# schemas
from src.schemas import RegisterInput, LoginInput, ProfileResponse, UserCreate, MeResponse

# routers 
user_router = APIRouter(prefix='/users', tags=['users'])
pdf_router = APIRouter(prefix='/pdfs', tags=['pdfs'])

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

  # fire a test task
  task = await fire_task(
    task_type= TaskTypes.TEST,
    payload={
      "message": "what's up!?"
    }
  )


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

# open a SSE connection -> server sent event
@pdf_router.get(path='/progress/{upload_id}')
async def progress_stream(
  request: Request,
  upload_id: str = Path(...),
  auth_user: User = Depends(dependency=auth_guard)
): 
  """ SSE endpoint that streams upload progress  for a given upload_id session """

  # generator 
  async def event_generator():

    # keep track of last percent upload -> used to avoid sending duplicated progress
    last_percent = None

    # create a Upload record
    upload = await Upload.find_one(Upload.upload_id == upload_id)

    # we start new upload process
    if not upload:
      upload = Upload(
        upload_id=upload_id,
        user=auth_user, # type: ignore
        percent=0, # initial progress
        status=UploadStatus.UPLOADING, # start an upload
      )
      # save in db
      await upload.insert()

    # our streaming loop -> as long as status = uploading -> yield the progress
    while True:
      # break if sse disconnected -> client is disconnected
      if await request.is_disconnected():
        break

      # get fresh db record -> with updated percent
      upload: Any = await Upload.find_one(Upload.upload_id == upload_id)

      # send data to frontend if:
        # upload_doc.percent , is updated 
        #or
        # upload_doc.status == done or failed -> to inform frontend at the end of upload.status

      if upload.percent != last_percent or upload.status in {UploadStatus.DONE, UploadStatus.FAILED}:
        # this is the payload we send to client 
        payload = dict(
          upload_id= upload.upload_id,
          percent= upload.percent, # we show this on our UI
          # convert enum to string -> json.dumps can't serialize Enum
          status= upload.status.value,
          file_id= upload.file_id,
          error= upload.error,
        )

        # we stream each chunk to the frontend
        # SSE -> expects lines starting with data: and terminated by two \n\n, mark the end of event
        # (EventSource in browser) -> receives this as event.data
        yield f"data: {json.dumps(payload)}\n\n"

        # we don't resend the same value next loop -> only if percent is changed from /pdf-upload route
        last_percent = upload.percent

      # stop streaming -> done, failed
      if upload.status in {UploadStatus.DONE, UploadStatus.FAILED}:
        print("stop streaming --")
        break

      await asyncio.sleep(1) # wait 1 seconds

  # run generator and yield each loop data to client
  return StreamingResponse(event_generator(), media_type='text/event-stream')
  
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket

# upload pdf route
@pdf_router.post("/upload-pdf")# 
async def upload_pdf(
  background_tasks: BackgroundTasks, # fastapi injects this 
  request: Request,
  # data: Any = Body(...),
  file: UploadFile = File(...),
  upload_id: str = Form(...),
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

  # upload progress record
  upload_doc = await Upload.find_one(Upload.upload_id == upload_id)

  if not upload_doc:
    upload_doc = Upload(
      upload_id=upload_id,
      percent=0,
      status=UploadStatus.UPLOADING,
      user=auth_user # type: ignore
    )
    await upload_doc.insert()

  else: # no Upload doc
    # in start of our upload -> reset everything
    upload_doc.percent = 0
    upload_doc.status = UploadStatus.UPLOADING
    upload_doc.file_id = None # gridfs_id

    await upload_doc.save()

  # background task: upload
  async def upload_chunks(
      file: UploadFile,
      upload_id: str ,
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
        print("\n******************\n\n")
        print(total_bytes)
        print("******************\n\n")
        if not chunk:
          break # not chunk left

        # write to gridfs
        await grid_in.write(data=chunk)

        # increment total chunk read
        total_bytes += len(chunk) # number of bytes

        # calculate upload.percent
        percent = math.floor((total_bytes / file_size) * 100)

        # update upload doc
        upload_doc = await Upload.find_one(Upload.upload_id == upload_id)
        # increase upload progress
        upload_doc.percent = min(percent, 100) # type: ignore

        await upload_doc.save() # type: ignore

        # some delay
        await asyncio.sleep(1)

      # close bucket
      await grid_in.close()

      # mark upload as done
      upload_doc: Any = await Upload.find_one(Upload.upload_id == upload_id)
      upload_doc.status = UploadStatus.DONE
      upload_doc.file_id =str(grid_in._id)
      upload_doc.percent = 100
      await upload_doc.save()

      # create a PDF doc -> metadata, text, html
      pdf_doc = PDF(
        filename=file.filename, # type: ignore
        gridfs_id=str(grid_in._id),
        upload_id=upload_id,
        user=user # type: ignore
      )
      
      await pdf_doc.insert()

    except Exception as e:
      print(str(e))
      # pdf upload failed
      upload_doc = await Upload.find_one(Upload.upload_id == upload_id)
      upload_doc.status = UploadStatus.FAILED # upload failed
      upload_doc.error = str(e)
      await upload_doc.save()

  # background task
  background_tasks.add_task(
    upload_chunks, # async process /function
    file,
    upload_id,
    user=auth_user
  )

  print(file.size, file_size)
  print('=---------------------------------')
  print(request.app.state.mongo_db)
  print(f"✅ Received file: {file.filename}")
  print(f"✅ Upload ID: {upload_id}")

  return dict(message="✅ pdf upload success")

  """
  upload_id = data['upload_id']

  # create or set a upload doc
  upload = await Upload.find_one(
    Upload.upload_id == upload_id,
  )

  if not upload:
    # create an upload
    upload = Upload(
      upload_id=upload_id,
      percent=0,
      status=UploadStatus.UPLOADING,
      user=auth_user,  # type: ignore
    )
    await upload.insert()
  else:
    # reset upload record
    upload.percent = 0
    upload.status = UploadStatus.UPLOADING
    upload.file_id = None

    await upload.save()
    
  # simulate background chunk process
  async def simulate_chunks(upload_id: str):
    for i in range(1, 11): # 10 steps
      # fake a delay
      await asyncio.sleep(0.5)

      # update upload with new percentage and date
      doc: Any = await Upload.find_one(Upload.upload_id == upload_id,)
      doc.percent = i * 10 # 10, 20, 30
      doc.updated_at = datetime.now(timezone.utc)

      await doc.save()

    # out of loop -> mark as done
    upload_doc: Any = await Upload.find_one(Upload.upload_id == upload_id)
    upload_doc.status = UploadStatus.DONE
    upload_doc.file_id = str(uuid.uuid4())

    await upload_doc.save()

  background_tasks.add_task(simulate_chunks, upload_id)

  return dict(
    message="upload started",
    upload_id=upload_id
  )
  """


