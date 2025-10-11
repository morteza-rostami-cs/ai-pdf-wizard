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

## Day 4 (WIP)

### ✅ Completed

- **Backend**

  - Added dependencies for route protection:
    - Authenticated-only routes
    - Guest-only routes
  - Enabled access to `auth_user` inside protected routes
  - Implemented `/logout` route to clear session cookie
  - Implemented `/me` route to return current authenticated user

- **Frontend**

  - Full **auth flow** integrated with backend
  - On page load, call `/me` to refresh auth state
  - Store current user in global `window.Auth` object
  - Added helpers:
    - `showIfAuth(...ids)` → show elements only to authenticated users
    - `showIfGuest(...ids)` → show elements only to guest users
  - Implemented `authGuard()` to redirect guests from protected pages
  - Implemented **logout** logic:
    - Clear global state
    - Call backend `/logout`
    - Redirect to `/login.html`
    - Added `attachLogoutButton()` helper to wire logout buttons

- **UI/UX**
  - Guest users see **Register/Login** buttons
  - Authenticated users see **Logout** button
  - Prevented UI flash by hiding content until auth state is resolved

### 🔜 Next

- Refine error/success handling for login/register
- Add toast/notification system for feedback
- Start building protected **profile page** with live user data

---

## Day 5 (WIP)

### ✅ Completed

- **Frontend: Profile Page**

  - Implemented **profile page** to display authenticated user data:

    - Email, plan type, and other user details.

  - Fetched data from `/me` on page load and injected into DOM.
  - Ensured that UI updates **only after auth state is confirmed**, preventing flash of unauthorized content.

- **Live PDF Upload Progress**

  - Implemented **SSE-based live progress bar** for PDF uploads:

    - Created `/pdfs/progress/{upload_id}` endpoint in FastAPI.
    - Backend streams **upload progress**, `percent`, and `status` in real-time.
    - Frontend uses `EventSource` to subscribe to updates and dynamically update UI.

  - Added `/upload-pdf` route to simulate upload chunks in background task for testing.
  - Used **MongoDB GridFS** to store files (preparing for actual PDF storage).

- **Challenges & Solutions**

  - **Cookie handling**:

    - Needed cookies for authenticated SSE.
    - Solved by serving frontend from **FastAPI** to share origin with backend.

  - **JSON serialization**:

    - Enum fields (`UploadStatus`) caused `json.dumps()` errors.
    - Solved by converting enum to string before streaming.

  - **Connection lifecycle**:

    - SSE closes when upload is done; handled cleanly on frontend to avoid errors.

  - **Shared state**:

    - Created or accessed `Upload` records in DB before streaming to avoid race conditions.

  - **Frontend-backend integration**:

    - Configured `EventSource` with `credentials: "include"` for cookies across SSE requests.
    - Ensured backend CORS and SameSite settings allowed cookies.

- **UI/UX**

  - Live upload progress bar updates dynamically from backend events.
  - Completed uploads automatically **close SSE connection** on frontend.
  - Users see **real-time progress** feedback instead of static loading indicators.

### 🔜 Next

- Implement actual **PDF chunked upload** and save in GridFS.
- Schedule **background text extraction** tasks after upload.
- Refine error handling for failed uploads.
- Connect progress bar to real file uploads rather than simulated ones.

---

### 🎥 Video

- [Issue #2 playlist](https://www.youtube.com/playlist?list=PLcccwZD44KFT7zot2XkPLcsBERHcIELzO)

---

## 🗓️ **Day 6 – PDF Upload System (Issue #3)**

**Main focus:** Building a full PDF upload flow with real-time progress feedback using SSE (Server-Sent Events).

### ✅ Completed Tasks

- Integrated **SSE connection** to stream real-time upload progress from the backend.
- Each upload session now uses a shared `upload_id` between `/upload-pdf` and `/progress` routes for synchronization.
- Implemented **frontend progress bar** that updates dynamically based on SSE events.
- Displayed **upload status messages** (in progress / completed / failed) in the UI.
- Continued improving integration between FastAPI background task and the frontend flow.

### 🎯 Next Steps

- Add error handling and cancel support for uploads.
- Trigger and manage a background **PDF processing job** after successful upload (next issue).

---

#### 🗓️ **Day 7 — Issue #3: PDF Upload System**

**Tasks Completed:**

- Added `PDFStatus` field in PDF model for progress tracking (upload, processing, embedding, etc.)
- Created `/pdfs/list` API route to retrieve all PDFs belonging to the logged-in user
- Implemented frontend logic to display the user’s uploaded PDFs and their current status

**Next Steps:**

- Implement download and delete endpoints
- Start PDF processing pipeline (text extraction, embedding)

---

## Day 8 — PDF Download & Frontend Refactor

### ✅ Completed

- Added `/download` backend route to fetch files from **GridFS**.
- Added **Download button** in frontend PDF list — users can now download their own uploaded PDFs.
- After each successful upload, a **background text-processing task** is automatically triggered (no implementation yet).
- 🧩 **Frontend Refactor:** Centralized all initialization logic into a single `main.js` entry point to avoid race conditions between scripts.

  - Handles global setup like `authGuard()` and `loadHeader()`.
  - Initializes shared promises (e.g., `currentUserPromise`) before page scripts run.
  - Dynamically loads page-specific modules based on `data-page`.

### 🧱 Result

- Smooth end-to-end upload and download flow.
- Stable and predictable frontend initialization for all pages.
- Foundation ready for upcoming **PDF text extraction pipeline**.

---

### 🧩 Day 9 — Issue #5: PDF Processing Pipeline (Extraction & Metadata Storage)

**Progress Summary:**
Implemented the core text extraction pipeline for uploaded PDFs.
When a user uploads a PDF, an asynchronous background task now processes the file, extracts both text and HTML for each page, and stores them in a new `PdfPage` model.

**✅ Completed Tasks**

- Added **PDF text extraction service** to handle page-by-page parsing.
- Introduced **PdfPage model** to store text and HTML for each page.
- Updated **async task handler** to run the extraction service after file upload.
- Linked extracted pages to their parent PDF record.
- Automatically updated the PDF’s **status** to `"embedding"` after extraction completes — preparing for the next pipeline stage.

**💡 Outcome:**
Each PDF is now decomposed into its individual pages, with structured text and HTML content ready for embedding or further semantic processing.

**🔗 Related Issue:** [#5 — PDF Processing Pipeline (Extraction & Metadata Storage)](../issues/5)
**🔗 Commit:** [`355b9ab`](../commit/355b9ab)

---

### 🎥 Video

- [Issue #3 playlist](https://www.youtube.com/playlist?list=PLcccwZD44KFT-CiYP_qLok74DWB_H_En9)

---

## Day 10 (WIP) — LangChain & Chroma Setup / Backend Refactor

### ✅ Completed

- **LangChain / Chroma prep**:

  - Implemented `prepare_page_for_embedding()` function to fetch PDF pages and prepare text + metadata for embedding.
  - Added `PageMetadata` dataclass for schema of metadata stored with each chunk in Chroma DB.
  - Skips PDFs that require OCR.
  - Handles per-page data for each PDF and associates it with the uploading user.

- **Backend folder refactor**:

  - Moved all `./backend` files to project root (`./`) for simpler structure.
  - Updated imports and paths accordingly.
  - No functional changes, purely organizational improvement.

### 🔜 Next

- Implement actual embedding with ChromaDB.
- Continue with pipeline for text embeddings and vector storage.
- Integrate embedding tasks with async PDF processing workflow.

---

### 🗓️ **Day 11 — PDF Embedding Pipeline Complete**

**Issue:** [#6 — PDF Embedding Pipeline (Chroma + Ollama + LangChain)](https://github.com/morteza-rostami-cs/ai-pdf-wizard/issues/6)
**Commit:** [`28bfcd5`](https://github.com/morteza-rostami-cs/ai-pdf-wizard/commit/28bfcd5)

#### ✅ Summary

Implemented the complete **PDF embedding pipeline**, connecting text extraction results with the vector database.
Each uploaded PDF is now embedded using a local LLM and stored in ChromaDB for future semantic retrieval.

#### 🔧 What’s Done

- Integrated **LangChain** for chunking per-page text into semantic units.
- Used **Ollama embeddings** to generate local vector representations.
- Persisted embeddings and metadata in **ChromaDB** (`data/chroma/pdf_chunks`).
- Implemented vector deletion by `pdf_id` for cleanup and reprocessing.
- End-to-end pipeline now covers:
  `Upload → Extraction → Embedding → Ready for Querying`.

#### 🚀 Outcome

PDFs are now fully prepared for vector search and intelligent question answering in the upcoming stages.

---

## 🧩 Day 12 — Centralized Event System (SSE → WebSocket)

**Goal:**
Implement a robust real-time event system for backend–frontend communication using pub/sub architecture.

### ✅ Achievements

- Designed and implemented an **in-memory `EventManager`** for managing real-time events.

  - Supports **per-user subscriptions**, **unsubscriptions**, and **broadcast publishing**.
  - Built on **`asyncio.Queue`** with locking for concurrency safety.
  - Includes global `event_manager` singleton instance.

- Added **SSE connection route** (`/sse`) integrated with the pub/sub system.

  - Real-time delivery of events to authenticated users.
  - Implemented **heartbeat**, **disconnect detection**, and **graceful unsubscribe**.
  - Added `/sse/test` route for publishing test events.

- Integrated **frontend with the centralized event system**.

  - Established persistent connection using `EventSource` (`connectSse()`).
  - Automatically connects only when the user is authenticated.
  - Handles open, message, custom events, and errors gracefully.

- Transitioned from **SSE to WebSocket** for improved reliability and bidirectional communication.

  - Solved FastAPI shutdown blocking caused by pending SSE generators.
  - Implemented proper cleanup, reconnection, and authentication handling for sockets.

### 🧠 Outcome

The system now supports **real-time event delivery** across the stack — enabling status updates, notifications, and live feedback with minimal overhead.
This marks the foundation for live PDF status streaming and other interactive features.

---

### 🎥 Video

- [Issue #3 playlist](https://www.youtube.com/playlist?list=PLcccwZD44KFQ7CQG5pBnGuLUsS2OsvjJw)
