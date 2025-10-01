

from fastapi import APIRouter, HTTPException, Depends, Response, Request, Body, Path, UploadFile, File, status, Query
from typing import Any
import random
import asyncio

# my imports
from src.models import User, Otp
from src.schemas import UserCreate
from src.services import fire_task
from src.dtos import TaskTypes, Dictor
from src.services import send_email

# schemas
from src.schemas import RegisterInput, LoginInput, ProfileResponse, AuthResponse

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
    user=payload['user_id'],
  ) 

  await otp_record.insert()

  return otp_record

# /users/register
@user_router.post(path="/register")
async def register(
  data: RegisterInput,
):
  # data
  email = data.email

  # create a user if does not exist
  user = await get_or_create_user(email=email)

  # generate otp code and store a record inside of db
  otp_record = await create_otp(payload={"user_id": user.id})

  # send email
  print(f"sending email: {user.email} - {otp_record.otp_code}")

  # send an email
  # asyncio.create_task(send_email(
  #   to_email=user.email,
  #   subject="Your OTP code", 
  #   body=f"hi, your otp code is : {otp_record.otp_code}"
  # ))

  return {"message": "register success", "otp_code": otp_record.otp_code}


@user_router.post(path="/login")
async def login(
  data: LoginInput,
):
  email = data.email
  otp_code = data.otp_code

  if not email or not otp_code:
    raise ValueError("missing input: email, otp_code")

  print("login request: ", data.model_dump())
  return {
    "message": "login route",
    "otp": otp_code
  }

@user_router.post(path="/logout")
async def logout(response: Response):
  
  # remove jwt from cookie
  print("logout request")

  return {
    "message": "register route",
  }

@user_router.get(path="/profile", response_model=ProfileResponse)
async def profile():
  print("profile request: ")
  return {
    "email": "example@gmail.com",
    "plan": "free",
  }

@user_router.post(path="/auth", response_model=AuthResponse)
async def auth():
  print("auth check request: ",)
  return {
    "authenticated": True
  }

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