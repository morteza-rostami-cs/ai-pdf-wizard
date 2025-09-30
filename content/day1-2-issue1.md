---

# 🚀 Issue #1 – Backend Foundation with FastAPI, MongoDB & Async Worker

In this milestone, we set up the **core backend infrastructure** for our AI PDF Wizard project.
The goal was to get the basics in place: configuration, database connection, models, routes, and a background worker.

---

## 1. Configuration with Pydantic Settings

We use [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) to manage environment variables like database URIs, JWT secrets, and freemium limits.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = ""
    MONGO_URI: str = ""
    MONGO_DB_NAME: str = ""
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""
    JWT_EXPIRE_MINS: int = 10
    OTP_EXPIRATION_MINUTES: int = 5

    FREE_MAX_PAGES: int = 20
    FREE_MAX_CHAT_TOKENS: int = 1000
    FREE_MAX_FILE_SIZE_MB: int = 5

    DEBUG: bool = True

    # Langchain / LLM
    LLM_MODEL: str = "gemma2:2b"
    LLM_URL: str = "http://127.0.0.1:11434"

    class Config:
        env_file = ".env"

settings = Settings()
```

✅ This gives us a **singleton** config instance available across the project.

---

## 2. MongoDB Integration

We use **Motor** (async MongoDB driver) + **Beanie ODM** for schema-based collections.

```python
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from src.models import User, Task

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

await init_beanie(
    database=db,
    document_models=[User, Task]
)

print("✅ MongoDb connected and Beanie initialized")
```

---

## 3. FastAPI App Setup

We configure CORS, a startup lifespan handler, and include our routers.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import user_router

app = FastAPI(
    title="AI PDF Wizard",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def index():
    return {"status": "ok", "message": "from /index route"}

# Register routers
app.include_router(user_router)
```

---

## 4. Models: User & Task

We start with two collections:

- **User** – for basic user data
- **Task** – a queue of async jobs for our worker

```python
from beanie import Document
from pydantic import EmailStr
from datetime import datetime, timezone

class User(Document):
    email: EmailStr
    name: str

    class Settings:
        name = "users"

class Task(Document):
    task_type: str
    status: str = "incomplete"
    retries: int = 0
    max_retries: int = 5
    created_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "tasks"
```

---

## 5. User Routes

A simple REST API to **create users** and **fetch all users**.

```python
from fastapi import APIRouter, Body
from src.models import User

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("")
async def get_users():
    return await User.find_all().to_list()

@user_router.post("")
async def create_user(user_in: dict = Body(...)):
    user = User(**user_in)
    await user.insert()
    return {"message": "user created", "user": user}
```

---

## 6. Async Task Worker

We built a **background worker loop** to process tasks in the `tasks` collection every few seconds.
This allows us to offload heavy jobs outside of API requests.

```python
import asyncio
from src.models import Task

async def process_task(task: Task):
    # fake processing
    print(f"Processing task: {task.task_type}")
    await task.mark_done()

async def task_worker_loop(interval: int = 5):
    while True:
        async for task in Task.find({"status": "incomplete"}):
            await task.mark_processing()
            asyncio.create_task(process_task(task))
        await asyncio.sleep(interval)
```

---

## ✅ Wrap-up

With this setup, we now have:

- Configuration management (`pydantic-settings`)
- MongoDB integration with `Motor + Beanie`
- Core models (`User`, `Task`)
- User API routes (GET, POST)
- Background worker for async jobs

This foundation is ready to expand in future issues (auth, AI features, file handling, etc.).
