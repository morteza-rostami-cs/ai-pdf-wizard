# AI PDF Wizard

A FastAPI + LangChain app for PDFs: upload, summarize, and chat with your documents. Frontend built with HTML/JS + Tailwind CSS.

## Tech Stack

- Backend: Python, FastAPI, LangChain, Ollama/OpenAI
- Database: MongoDB (GridFS)
- Vector DB: Chroma
- Frontend: HTML, JavaScript, Tailwind CSS, Flowbite
- Deployment: VPS with Nginx

## 🚀 Features (MVP / Planned)

- [x] **Initial Project Setup & Infrastructure**

  - FastAPI backend, MongoDB connection, ChromaDB integration, async worker loop
  - `.env` config with Pydantic
  - Basic frontend (HTML + JS + Tailwind CDN) connected to backend test route

- [issue #1 video](https://www.youtube.com/playlist?list=PLcccwZD44KFTqjAzkfjA97K67fIOMJy2i)

- [ ] **Authentication & User Management**

  - User registration with email + OTP (via Gmail SMTP)
  - Login with OTP → issue JWT in HttpOnly cookie
  - Logout & `/auth` check route
  - Protected & guest routes (backend + frontend guards)
  - Profile page with user info & avatar upload
  - Subscription scaffolding: `plan: "free"`, `usage: { pdfUploads, chatTokens }`

- [ ] **PDF Upload & Management**

  - Upload PDFs (GridFS or filesystem + metadata in Mongo)
  - Show upload progress & status (uploaded / processing / embedding / ready / failed)
  - List uploaded PDFs in user dashboard
  - Delete PDFs

- [ ] **PDF Processing Pipeline**

  - Extract text + per-page HTML from PDFs
  - Store text + HTML + metadata in MongoDB
  - Background task queue for extraction, embedding, and summarization

- [ ] **Vectorization & Embeddings**

  - Chunk extracted text and generate embeddings
  - Store vectors + metadata in ChromaDB
  - Ensure per-user isolation of vector data

- [ ] **Summarization**

  - Generate summaries via LLM (short, detailed, bullet styles)
  - Show progress (loading → complete)
  - Store summaries for reuse
  - Export summary (copy/download)

- [ ] **Chat with PDF (RAG)**

  - Start new chat linked to a PDF
  - Query using RAG (vector retrieval + LLM answer)
  - Continue previous chats with history loaded from Mongo
  - Delete chat sessions

- [ ] **User Dashboard**

  - Display user PDFs, summaries, chats, and usage stats
  - Manage profile, files, and chats in one place

- [ ] **Freemium & Subscription System**

  - Free plan limits: number of PDFs, chat tokens, etc.
  - Paid plans: unlock higher limits, faster processing, advanced features
  - Payment integrations (Stripe/PayPal + optional crypto)
  - Backend enforcement of plan limits

- [ ] **Admin & Monitoring**

  - View users, subscriptions, and usage
  - Monitor background tasks and processing status
  - Error handling, logs, and retries for failed tasks

- [ ] **Deployment & Scaling**

  - Docker setup (backend, frontend, worker, databases)
  - Deploy with SSH → clone → `docker-compose up -d`
  - Put services behind Nginx reverse proxy with domain + SSL
  - Production-ready MongoDB + Chroma setup

- [ ] **Documentation & Demos**

  - Walkthroughs for each feature in README/docs
  - Demo videos showcasing features

## PROGRESS

See [PROGRESS.md](./PROGRESS.md)
