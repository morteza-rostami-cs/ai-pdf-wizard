from fastapi import FastAPI
from typing import Any
from contextlib import asynccontextmanager
import motor.motor_asyncio
from beanie import init_beanie # type: ignore
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
import asyncio

# my imports ------------------------
from src.config import settings
from src.models import User, Task
from src.workers import task_worker_loop


# my routes --------------------------
from src.routes import user_router

# lifespan -> runs on server start 
@asynccontextmanager
async def lifespan(app: FastAPI):
  """ this runs on app startup """

  client: AsyncIOMotorClient[Any] = motor.motor_asyncio.AsyncIOMotorClient(
    host=settings.MONGO_URI,
  )

  # instance of database
  db: AsyncIOMotorDatabase[Any] = client[settings.MONGO_DB_NAME]

  # save db instance globally 
  from src import config

  config.mongo_client = client
  config.mongo_db = db

  # register models
  await init_beanie(
    database=db, # type: ignore
    document_models=[User, Task]
  )

  # mongodb is connected
  print("✅ MongoDb connected and beanie initialized")

  # here -> we setup our async worker (later)

  if db == None:
    raise Exception("mongo instance is None.")

  asyncio.create_task(
    task_worker_loop(
      db=db,
      interval=5  # 5 seconds
    )
  )
  

  yield # everything after this , runs on shutdown

  # close mongodb
  client.close()
  print("✅ MongoDB connection closed")

# fast api app
app = FastAPI(
  title="ai pdf wizard",
  version="0.1.0",
  # pass lifespan
  lifespan=lifespan
)

# /index 
@app.get('/')
async def index() -> Any:

  return {
    "status": "ok",
    "message": "from /index route",
    "db_name": settings.MONGO_DB_NAME,
  }

# --------------------------
# routes
# --------------------------

app.include_router(router=user_router)

# run fastapi server
if __name__ == "__main__":
  import uvicorn

  uvicorn.run(
    "src.main:app",
    host="0.0.0.0",
    port=8000,
    reload=True
  )