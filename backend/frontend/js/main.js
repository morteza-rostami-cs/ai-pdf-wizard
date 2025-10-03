import { fetchAuthUser, showIfAuth, showIfGuest } from "./auth/auth.js";

// load auth user from backend, set promise on window
document.addEventListener("DOMContentLoaded", () => {
  window.currentUserPromise = fetchAuthUser();
});

const source = new EventSource("http://localhost:8000/api/pdfs/progress/123");

source.onmessage = (event) => {
  const payload = JSON.parse(event.data);

  console.log("progress: ", payload.percent, payload.status);

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
