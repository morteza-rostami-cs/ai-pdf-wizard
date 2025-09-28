# AI PDF Wizard

A FastAPI + LangChain app for PDFs: upload, summarize, and chat with your documents. Frontend built with HTML/JS + Tailwind CSS.

## Tech Stack

- Backend: Python, FastAPI, LangChain, Ollama/OpenAI
- Database: MongoDB (GridFS)
- Vector DB: Chroma
- Frontend: HTML, JavaScript, Tailwind CSS, Flowbite
- Deployment: VPS with Nginx

## Features (MVP / Planned)

- [ ] User authentication (OTP + JWT cookie)
- [ ] Upload PDF & store in GridFS
- [ ] Show upload progress & status: uploaded / processing / embedding / ready / failed
- [ ] Extract text & per-page HTML from PDF
- [ ] Vectorize PDF & store in vector db
- [ ] Summarize PDF (progress shown)
- [ ] Chat with PDF content
- [ ] Store & load chat sessions
- [ ] Delete chat sessions
- [ ] PDF/Session management APIs
- [ ] Background processing for heavy tasks (PDF processing, embeddings)
- [ ] Logs, error handling, validations
- [ ] Content walkthroughs for each feature
- [ ] Demo videos for each feature

## PROGRESS

See [PROGRESS.md](./PROGRESS.md)
