from fastapi import FastAPI
from typing import Any
from contextlib import asynccontextmanager
import motor.motor_asyncio
from beanie import init_beanie # type: ignore
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
import asyncio

from fastapi.middleware.cors import CORSMiddleware

# my imports ------------------------
from src.config import settings
from src.models import User, Task, Otp, Upload, PDF, PdfPage
from src.workers import task_worker_loop


# my routes --------------------------
from src.routes import user_router, pdf_router

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
  #from src import config

  #config.mongo_client = client
  #config.mongo_db = db

  # store client and db in app.state
  app.state.mongo_client = client
  app.state.mongo_db = db

  # register models
  await init_beanie(
    database=db, # type: ignore
    document_models=[User, Task, Otp, Upload, PDF, PdfPage]
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



# allowed origins
origins = [
  "http://127.0.0.1:5500",
  "http://localhost:5500",
  "http://localhost:5500",
]

# middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True, # cookie
  allow_methods=["*"],
  allow_headers=["*"],
)

# /index 
# @app.get('/')
# async def index() -> Any:

#   return {
#     "status": "ok",
#     "message": "from /index route",
#     "db_name": settings.MONGO_DB_NAME,
#   }

# --------------------------
# routes
# --------------------------

app.include_router(router=user_router, prefix='/api')
app.include_router(router=pdf_router, prefix='/api')

from fastapi.staticfiles import StaticFiles
# has to come after other /api routes
app.mount("/", StaticFiles(directory='frontend', html=True), name='frontend')

# run fastapi server
if __name__ == "__main__":
  import uvicorn

  uvicorn.run(
    "src.main:app",
    host="0.0.0.0",
    port=8000,
    reload=True
  )