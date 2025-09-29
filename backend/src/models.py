from beanie import Document
from pydantic import BaseModel, EmailStr

#-----------------------
# User model
#-----------------------

class User(Document):
  email: EmailStr
  name: str

  class Settings:
    name  = 'users'# name of collection
