import { socketBus } from "./sockets.js";
import { fetchPDFs } from "./pdfService.js";

export function initUploadProgress() {
  const uploadList = document.querySelector("#upload-list");

  // listen to upload_progress updates
  socketBus.addEventListener("upload_progress", function (e) {
    const data = e.detail;
    // update ui
    updateUploadUI(data);
  });

  // listen for done and failed
  socketBus.addEventListener("upload_done", function (e) {
    const data = e.detail;
    markUploadDone(data);
  });

  socketBus.addEventListener("upload_failed", function (e) {
    const data = e.detail;
    markUploadFailed(data);
  });

  function updateUploadUI(data) {
    // Upload
    const { id, percent, status } = data;

    // find upload element
    let uploadEl = document.querySelector(`[data-upload-id="${id}"]`);

    if (!uploadEl) {
      uploadEl = document.createElement("div");
      // set data-upload-id
      uploadEl.dataset.uploadId = id;

      uploadEl.innerHTML = `
        <div class="upload-item">
          <span>${id}</span>
          <progress value="${percent}" max="100"></progress>
          <span class="status">${status}</span>
        </div>
      `;

      // push into uploadList
      uploadList.appendChild(uploadEl);
    } else {
      // upload element exists
      const progressEl = uploadEl.querySelector("progress");
      const statusEl = uploadEl.querySelector(".status");

      // update progress & status
      progressEl.value = percent;
      statusEl.textContent = status;
    }
  }

  function markUploadDone(data) {
    const uploadEl = document.querySelector(`[data-upload-id="${data.id}"]`);
    if (uploadEl) uploadEl.querySelector(".status").textContent = "✅ done";

    // after upload done -> fetch all pdfs
    fetchPDFs();
  }

  function markUploadFailed() {
    const uploadEl = document.querySelector(`[data-upload-id="${data.id}"]`);
    if (uploadEl) uploadEl.querySelector(".status").textContent = "❌ failed";
  }

  console.log("=== ready for upload progress events ===");
}

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
