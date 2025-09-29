from beanie import Document, PydanticObjectId
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone, timedelta

# my imports 
from src.dtos import Dictor

#-----------------------
# User model
#-----------------------

class User(Document):
  email: EmailStr
  name: str

  class Settings:
    name  = 'users'# name of collection

#-----------------------
# Task model
#-----------------------
from src.dtos import TaskTypes, TaskStatus

class Task(Document):
  task_type: TaskTypes
  status: TaskStatus = Field(default=TaskStatus.INCOMPLETE)
  payload: Dictor # dynamic data dictionary 
  retries: int = Field(default=0)
  max_retries: int = Field(default=5)
  error: Optional[str] = None

  created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  completed_at: Optional[datetime] = None

  class Settings: 
    name = "tasks"

  async def mark_processing(self):
    """ mark a task processing by the worker """
    self.status = TaskStatus.PROCESSING
    self.updated_at = datetime.now(timezone.utc)
    await self.save()

  async def mark_done(self):
    """ mark a task as done, processed by the worker """
    self.status = TaskStatus.DONE
    self.completed_at = datetime.now(timezone.utc)
    self.updated_at = datetime.now(timezone.utc)
    await self.save()

  async def mark_failed(self, error_msg: str):
    """ 
     if: max_retries -> status = failed
     else: status = incomplete
    """

    self.error = error_msg
    self.retries += 1

    if self.retries < self.max_retries:
      # failed and done!
      self.status = TaskStatus.FAILED
    else:
      # still can try
      self.status = TaskStatus.INCOMPLETE
    
    self.updated_at = datetime.now(timezone.utc)
    await self.save()
