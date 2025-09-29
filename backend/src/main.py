from fastapi import FastAPI
from typing import Any
#from contextlib import asynccontextmanager


# lifespan -> runs on server start 
# @asynccontextmanager
# async def lifespan(app: FastAPI):

# fast api app
app = FastAPI(
  title="ai pdf wizard",
  version="0.1.0",
)

# /index 
@app.get('/')
async def index() -> Any:

  return {
    "status": "ok",
    "message": "from /index route"
  }

# run fastapi server
if __name__ == "__main__":
  import uvicorn

  uvicorn.run(
    "src.main:app",
    host="0.0.0.0",
    port=8000,
    reload=True
  )