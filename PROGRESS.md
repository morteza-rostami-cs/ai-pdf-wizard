# Project Progress Log

All daily logs of implemented features, videos, and next steps.

## Day 1 — Initial Setup & Backend Basics

### Completed:

- Scaffolded FastAPI project with initial folder structure and `main.py`.
- Added `requirements.txt` and installed necessary packages.
- Configured `.env` and Pydantic `Settings` class for environment variables.
  - ⚠️ Fixed Pydantic v2 `extra_forbidden` error by matching `.env` keys to Settings fields.
- Connected MongoDB using Beanie ODM.
- Created a basic `User` model.
- Implemented test routes:
  - `POST /users` → writes a record to MongoDB
  - `GET /users` → reads a record from MongoDB
- Setup async worker loop with a sample test task.
- Created `Task` model and handler to trigger tasks from routes.

### Notes / Challenges:

- Learned about Pydantic v2 strict extra fields behavior.
- Verified async worker can run tasks triggered from different endpoints.

### Next:

- Setup first real backend feature (PDF upload route + processing scaffold).
- Connect frontend to display test data and worker task status.

### Video:

- [Day 1 Progress Demo](https://youtu.be/dummy123)

## Day 2 (WIP)

### ✅ Completed

- Setup minimal frontend file & folder structure
- Added `index.html` with TailwindCSS via CDN
- Implemented basic header and navigation
- Created centralized fetch utility
- Connected frontend to backend with test `GET /users` route
- Rendered users in UI
- Fixed CORS issue by enabling FastAPI `CORSMiddleware`

### 🔑 Issue #2 (Auth system) progress

- Backend:

  - Added new fields to `User` model
  - Created `Otp` model for OTP-based login
  - Implemented auto-delete of expired OTPs in MongoDB
  - Setup backend routes with strict input/output types:
    - `POST /register`
    - `POST /login`
    - `GET /profile`
    - `POST /logout`
    - `POST /auth` (auth check via HTTP-only cookie)

- Frontend:
  - Built **register form** UI
  - Implemented form handling and validation
  - Successfully submitted email to backend `/register` route

### 🔜 Next

- Complete frontend login form and connect to backend `/login`
- Handle JWT HTTP-only cookies for session management
- Build protected profile page showing user info
- Add error/success handling for registration/login
