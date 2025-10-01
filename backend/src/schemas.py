from pydantic import BaseModel, EmailStr
from typing import Optional

# my imports 
from src.models import User

# ===============
# auth/users schemas
# ===============

class UserCreate(BaseModel):
  """ POST: /users """
  email: EmailStr
  name: str 

# /register
class RegisterInput(BaseModel):
  email: EmailStr

# /login -> input
class LoginInput(BaseModel):
  email: EmailStr
  otp_code: str

# /profile -> response
class ProfileResponse(BaseModel):
  email: EmailStr
  plan: str

# /auth -> response
class AuthResponse(BaseModel):
  authenticated: bool
  user: Optional[User] = None

