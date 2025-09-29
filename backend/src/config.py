
# pydantic config

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  ENV: str = ''

  # mongodb
  MONGO_URI: str = ''
  MONGO_DB_NAME: str = ''

  # freemium limits 
  FREE_MAX_PAGES: int = 20
  FREE_MAX_CHAT_TOKENS: int = 1000
  FREE_MAX_FILE_SIZE_MB: int = 5

  # jwt/auth
  JWT_SECRET_KEY: str = ""
  JWT_ALGORITHM: str = ''
  JWT_EXPIRE_MINS: int = 10
  OTP_EXPIRATION_MINUTES: int = 5

  # other 
  DEBUG: bool = True

  # langchain 
  LLM_MODEL: str = "gemma2:2b"
  LLM_URL: str = "http://127.0.0.1:11434"
  # embedding model
  EMBED_MODEL: str ="mxbai-embed-large"

  # chroma db -> ./storage
  CHROMA_PERSIST: str = ''

  # pdf storage
  PDF_STORAGE: str = ''

  # smtp email sending
  SMTP_HOST: str= ''
  SMTP_PORT: int = 2000
  SMTP_USER: str= ''
  SMTP_PASS: str= ''
  SMTP_FROM: str= ''

  MAX_RETRIES: int = 5

  class Config:
    env_file = '.env' # load from .env file

# singleton -> one instance of settings
settings = Settings()

# =================== mongo db instance ================

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Any

# mongo global instance
mongo_client: AsyncIOMotorClient[Any] | None = None
mongo_db: AsyncIOMotorDatabase[Any] | None = None