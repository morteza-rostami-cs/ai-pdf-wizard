

from fastapi import APIRouter, HTTPException, Depends, Response, Request, Body, Path, UploadFile, File, status, Query
from typing import Any

# my imports
from src.models import User
from src.schemas import UserCreate
from src.services import fire_task
from src.dtos import TaskTypes

# routers 
user_router = APIRouter(prefix='/users', tags=['users'])

#==============
# User routes
#==============

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