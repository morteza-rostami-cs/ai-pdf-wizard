import { api } from "../api.js";
import { openSseProgress, updateProgressBar } from "../upload-progress.js";

// pdf form
const form = document.getElementById("pdf-form");

form.addEventListener("submit", async (event) => {
  console.log("start pdf upload");
  event.preventDefault();

  const upload_id = crypto.randomUUID();

  // open a sse connection -> to get upload progress
  openSseProgress(upload_id, updateProgressBar);

  // file input
  const fileEl = document.getElementById("pdf-input");

  // submit button
  const submitBtnEl = document.getElementById("pdf-upload-submit-btn");

  // file
  const file = fileEl.files[0];

  //const upload_id = "123";

  if (!file) {
    window.alert("please select a file first!");
    return;
  }

  // formdata
  const formData = new FormData();

  formData.append("file", file);
  formData.append("upload_id", upload_id);
  formData.append("file_size", file.size);

  // loading state
  submitBtnEl.textContent = "";
  submitBtnEl.disabled = true;
  submitBtnEl.textContent = "Loading...";

  // request
  try {
    const data = await api.pdfUpload(formData);

    // success
  } catch (err) {
    console.log("pdf upload failed, ", err);
  } finally {
    submitBtnEl.textContent = "Upload";
    submitBtnEl.disabled = false;
  }
});
