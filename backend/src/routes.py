

from fastapi import APIRouter, HTTPException, Depends, Response, Request, Body, Path, UploadFile, File, status, Query
from typing import Any
import random
import asyncio
# from bson import ObjectId
from datetime import datetime, timezone
from beanie import PydanticObjectId
from bson import DBRef

# my imports
from src.models import User, Otp
from src.services import fire_task
from src.dtos import TaskTypes, Dictor
from src.services import send_email, generate_jwt, verify_jwt, verify_token
from src.config import settings
from src.dependencies import auth_guard, guest_guard

# schemas
from src.schemas import RegisterInput, LoginInput, ProfileResponse, UserCreate, MeResponse

# routers 
user_router = APIRouter(prefix='/users', tags=['users'])

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
    max_age=settings.JWT_EXPIRE_MINS,
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
  return dict(email=auth_user.email, plan="free")

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