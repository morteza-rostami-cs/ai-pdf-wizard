---

### **Blog: Implementing Live PDF Upload Progress with SSE in FastAPI**

#### **File Creation Command**

```bash
touch content/2025-10-03-live-pdf-upload-progress.md
```

---

# Implementing Live PDF Upload Progress in FastAPI with SSE

In this post, I’ll walk through how I implemented **real-time PDF upload progress** in my FastAPI app, challenges I faced, and how I overcame them. The frontend uses **plain HTML/JS with Tailwind**, and the backend is **FastAPI + MongoDB + Beanie**.

---

## **1. Problem Statement**

I wanted a **PDF upload feature** that:

- Shows a **live progress bar** on the frontend.
- Updates in **real-time from the backend**.
- Stores files in **MongoDB GridFS**.
- Keeps track of all user uploads in a **Mongo collection**.
- Allows **download by file ID**.
- Schedules background processing after upload completion.

The tricky part? **Streaming progress updates live to the frontend with authentication**.

---

## **2. Backend Setup**

### **Upload Model**

We created a `Upload` model to track upload progress:

```python
from beanie import Document, Link
from datetime import datetime, timezone
from enum import Enum

class UploadStatus(str, Enum):
    UPLOADING = "UPLOADING"
    DONE = "DONE"
    FAILED = "FAILED"

class Upload(Document):
    upload_id: str
    user: Link[User]
    percent: int = 0
    status: UploadStatus = UploadStatus.UPLOADING
    file_id: str | None = None
    created_at: datetime = datetime.now(timezone.utc)
```

- `percent`: tracks upload progress.
- `status`: uses an Enum for upload state.
- `file_id`: stores GridFS file reference after upload.

---

### **SSE Route**

We implemented an SSE endpoint to **stream progress**:

```python
from fastapi.responses import StreamingResponse

@pdf_router.get('/progress/{upload_id}')
async def progress_stream(request: Request, upload_id: str, auth_user: User = Depends(auth_guard)):
    async def event_generator():
        last_percent = None
        upload = await Upload.find_one(Upload.upload_id == upload_id)

        if not upload:
            upload = Upload(upload_id=upload_id, user=auth_user)
            await upload.insert()

        while True:
            if await request.is_disconnected():
                break

            upload = await Upload.find_one(Upload.upload_id == upload_id)
            if upload.percent != last_percent or upload.status in {UploadStatus.DONE, UploadStatus.FAILED}:
                yield f"data: {json.dumps({ 'percent': upload.percent, 'status': upload.status.value, 'file_id': upload.file_id })}\n\n"
                last_percent = upload.percent

            if upload.status in {UploadStatus.DONE, UploadStatus.FAILED}:
                break

            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type='text/event-stream')
```

**Key points:**

- Uses `StreamingResponse` with `text/event-stream`.
- Converts `UploadStatus` enum to `.value` for JSON serialization.
- Keeps looping until upload is `DONE` or `FAILED`.
- Checks for **disconnection** with `request.is_disconnected()`.

---

### **Upload Route**

The upload route triggers a **background task** simulating upload:

```python
from fastapi import BackgroundTasks

@pdf_router.post("/upload-pdf")
async def upload_pdf(background_tasks: BackgroundTasks, data: Any, auth_user: User = Depends(auth_guard)):
    upload_id = data['upload_id']
    upload = await Upload.find_one(Upload.upload_id == upload_id)

    if not upload:
        upload = Upload(upload_id=upload_id, user=auth_user)
        await upload.insert()
    else:
        upload.percent = 0
        upload.status = UploadStatus.UPLOADING
        upload.file_id = None
        await upload.save()

    async def simulate_chunks(upload_id: str):
        for i in range(1, 11):
            await asyncio.sleep(0.5)
            doc = await Upload.find_one(Upload.upload_id == upload_id)
            doc.percent = i * 10
            await doc.save()

        doc = await Upload.find_one(Upload.upload_id == upload_id)
        doc.status = UploadStatus.DONE
        doc.file_id = str(uuid.uuid4())
        await doc.save()

    background_tasks.add_task(simulate_chunks, upload_id)

    return {"message": "upload started", "upload_id": upload_id}
```

---

## **3. Frontend Integration**

Plain JS with `EventSource`:

```javascript
const source = new EventSource("/api/pdfs/progress/123");

source.onmessage = (event) => {
  const payload = JSON.parse(event.data);
  console.log("progress:", payload.percent, payload.status);

  document.getElementById("progress-bar").style.width = payload.percent + "%";

  if (["done", "failed"].includes(payload.status.toLowerCase())) {
    source.close();
    console.log("SSE connection closed by client");
  }
};

source.onerror = (err) => {
  console.error("SSE error", err);
  source.close();
};
```

- Updates progress bar in real-time.
- Closes SSE connection when upload finishes or fails.

---

## **4. Major Challenges & Solutions**

1. **Cookie Authentication Across Ports**

   - Problem: Frontend on `localhost:5500`, backend on `localhost:8000`.
   - Solution: Serve frontend via FastAPI (`StaticFiles`) for **same-origin**.

2. **SSE & Cookie Sending**

   - Problem: `EventSource` doesn't send cookies cross-origin by default.
   - Solution: Same-origin approach allows cookies to be sent automatically.

3. **JSON Serialization of Enums**

   - Problem: `UploadStatus` enums were not serializable.
   - Solution: Convert to string using `.value` before `json.dumps()`.

4. **Shared State**

   - Problem: SSE generator needs `Upload` record before background task updates.
   - Solution: SSE route **creates `Upload` record if missing**.

5. **Handling SSE Disconnects**

   - Problem: Connection may drop mid-upload.
   - Solution: Use `request.is_disconnected()` in backend and close `EventSource` on frontend.

6. **Plain JS Frontend**

   - Problem: No React/Vue → manually parse JSON and update DOM.
   - Solution: `EventSource` + `onmessage` + `onerror` listeners.

---

## **5. Key Takeaways**

- **Serving frontend from backend solves cross-origin & cookie issues.**
- **SSE is effective for live progress updates.**
- Always handle **enum serialization** for JSON.
- Background tasks + DB records allow shared state between frontend and SSE generator.

---

## **6. Next Steps**

- Replace simulated upload with **real GridFS PDF upload**.
- Add **text extraction** and **PDF processing pipeline**.
- Show multiple uploads in a **dashboard** with real-time progress bars.

---

## **Commit Message**

```
feat: implement live SSE PDF upload progress with backend and frontend integration

- Added Upload model to track progress
- SSE route /progress/{upload_id} streams live upload updates
- Upload route /upload-pdf simulates chunked upload with background tasks
- Frontend uses EventSource to show live progress bar
- Moved frontend folder into backend to unify origin (cookies + SSE)
- Solved enum JSON serialization, disconnect handling, and shared state issues
```
