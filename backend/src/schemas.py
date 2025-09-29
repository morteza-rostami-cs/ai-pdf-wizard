from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
  """ POST: /users """
  email: EmailStr
  name: str 
