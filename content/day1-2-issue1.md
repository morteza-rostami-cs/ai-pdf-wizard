# Issue #1 — Fullstack Setup: FastAPI + Frontend Integration

## Overview

This feature covers the initial backend and frontend setup, connecting them for the first time, and testing basic API calls from the frontend. It includes tasks from Day 1 and Day 2.

---

## Day 1 — Backend Setup

### Tasks Completed

- Created project file structure with `main.py`, `requirements.txt`, `.gitignore`, `README.md`, and `PROGRESS.md`.
- Setup `.env` and **Pydantic Settings** for environment variables.
- Connected **MongoDB** with Beanie.
- Created a basic `User` model.
- Implemented `/test` routes (GET/POST) to verify database connectivity.
- Setup **async worker loop** with a test task and a `Task` model.

### Challenges

- Encountered Pydantic v2 `extra_forbidden` error when loading `.env` variables.
- Resolved by adding missing fields to the Settings class.

### Takeaways

- FastAPI backend successfully running.
- MongoDB integration working.
- Async worker tested and functional.

---

## Day 2 — Frontend Setup & Integration

### Tasks Completed

- Created **frontend file & folder structure**.
- Added `index.html` with **TailwindCSS via CDN**.
- Implemented basic header and navigation.
- Created **centralized fetch utility** in JavaScript.
- Tested `GET /users` API call and rendered results in the UI.
- Encountered **CORS error**, solved by adding FastAPI `CORSMiddleware`.

### Challenges

- Handling CORS when calling backend from frontend.
- Solution: enabled `CORSMiddleware` in FastAPI with proper origins.

### Takeaways

- Frontend connected successfully to backend.
- Basic rendering of backend data on frontend verified.
- Ready to start next feature: **Auth system**.

---

## Resources

- Video demonstration: [YouTube dummy link](https://youtu.be/dummy123)
- Related issue: [Issue #1](https://github.com/<your-repo>/issues/1)
