# Project Progress Log

All daily logs of implemented features, videos, and next steps.

---

## Day 1 — Initial Setup & Backend Basics

### ✅ Completed

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

### 📝 Notes / Challenges

- Learned about Pydantic v2 strict extra fields behavior.
- Verified async worker can run tasks triggered from different endpoints.

### 🔜 Next

- Setup first real backend feature (PDF upload route + processing scaffold).
- Connect frontend to display test data and worker task status.

---

## Day 2 (WIP)

### ✅ Completed

- Setup minimal frontend file & folder structure
- Added `index.html` with TailwindCSS via CDN
- Implemented basic header and navigation
- Created centralized fetch utility
- Connected frontend to backend with test `GET /users` route
- Rendered users in UI
- Fixed CORS issue by enabling FastAPI `CORSMiddleware`

### 🎥 Video

- [Issue #1 playlist](https://www.youtube.com/playlist?list=PLcccwZD44KFTqjAzkfjA97K67fIOMJy2i)

---

### 🔑 Issue #2 — Authentication & User Management (In Progress)

#### Backend

- Added new fields to `User` model
- Created `Otp` model for OTP-based login
- Implemented auto-delete of expired OTPs in MongoDB
- Setup backend routes with strict input/output types:
  - `POST /register`
  - `POST /login`
  - `GET /profile`
  - `POST /logout`
  - `POST /auth` (auth check via HTTP-only cookie)

#### Frontend

- Built **register form** UI
- Implemented form handling and validation
- Successfully submitted email to backend `/register` route

---

### 🔜 Next

- Complete frontend login form and connect to backend `/login`
- Handle JWT HTTP-only cookies for session management
- Build protected profile page showing user info

---

## Day 3 — Authentication & User Management (Issue #2)

### ✅ Completed

**Backend:**

- Added `/register` route to accept email, generate OTP, and store in MongoDB.
- Integrated Gmail SMTP to send OTPs to user inbox.
- Implemented `/login` route to accept email + OTP.
- `/login` route validates OTP and sets JWT in an HTTP-only cookie.
- Fixed Beanie TTL index issue for OTP auto-expiry.
- Fixed DBRef query issue for OTP lookup.
- Fixed cookie persistence issue in development (localhost vs 127.0.0.1).

**Frontend:**

- Built registration form and OTP request UI.
- Implemented login form to submit email + OTP.
- Verified successful login sets JWT cookie in browser.

### 🔧 Notes / Challenges

- Learned about MongoDB TTL index setup with Beanie.
- Debugged DBRef vs ObjectId querying in Beanie.
- Handled cross-origin cookie persistence issues in development.

### 🔜 Next

- Complete login form error/success handling on frontend.
- Build protected profile page showing user information.
- Start session management with JWT verification.

---
