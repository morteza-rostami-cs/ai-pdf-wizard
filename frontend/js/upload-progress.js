/**
 * open a SSE connection for fetching upload progress
 * */
/*
export function openSseProgress(upload_id, onUpdate) {
  // SSE -> localhost:8000 , localhost:5500
  const source = new EventSource(
    `http://localhost:8000/api/pdfs/progress/${upload_id}`
  );

  // GET a message from server
  source.onmessage = (event) => {
    const payload = JSON.parse(event.data);

    // console.log("progress: ", payload.percent, payload.status);

    // update progress on ui
    onUpdate(payload);

    if (
      payload.status?.toLowerCase() === "done" ||
      payload.status?.toLowerCase() === "failed"
    ) {
      // close connection
      source.close();
      console.log("SSE connection closed by client");
    }
  };

  source.onerror = (err) => {
    console.error("SSE error", err);
    // connection failed -> close connection
    source.close();
  };
}
*/
/**
 * takes payload and update progress-bar ui
 * */
export function updateProgressBar(payload) {
  //data
  const percent = payload.percent;
  const status = payload.status;

  // elements
  const progressEl = document.getElementById("progress-bar");
  const statusTxtEl = document.getElementById("upload-status");

  if (!progressEl) return;

  // update progress bar
  progressEl.style.width = `${percent}%`;
  progressEl.textContent = `${percent}%`;

  if (status.toLowerCase() === "done") {
    progressEl.className = "bg-green-500 h-4 rounded-md transition-all";
    statusTxtEl.textContent = "✅ upload completed";
  } else if (status.toLowerCase() === "failed") {
    progressEl.className = "bg-red-500 h-4 rounded-md transition-all";
    statusTxtEl.textContent = "❌ Upload failed";
  } else {
    // uploading
    progressEl.className = "bg-blue-500 h-4 rounded-md transition-all";
    statusTxtEl.textContent = "uploading...";
  }
}
