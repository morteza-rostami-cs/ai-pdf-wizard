from pydantic import BaseModel, EmailStr
from typing import Optional
from dataclasses import dataclass

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

# /me -> response
class MeResponse(BaseModel):
  authenticated: bool
  user: Optional[User] = None

# schema for page chunk metadata
@dataclass
class PageMetadata:
  """ an schema for page metadata we store along with each chunk in chroma db """
  pdf_id: str # PDF
  user_id: str
  page_number: int
  total_pages: int
  filename: str
  #file_path: str
  uploaded_at: str # ISO datetime
  source: str = "user_upload"
  chunk_origin: str = "page_level" # page and chapter

