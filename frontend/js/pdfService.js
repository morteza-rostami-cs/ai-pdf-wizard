import { api } from "./api.js";
import { socketBus } from "./sockets.js";

// pdf_status_update
function initPdfEvents() {
  const uploadList = document.querySelector("#upload-list");

  // listen to upload_progress updates
  socketBus.addEventListener("pdf_status_update", function (e) {
    const data = e.detail;
    // update ui
    updatePdfStatus(data);
  });

  function updatePdfStatus(data) {
    console.log("----update pdf status--------*8", data);

    const { id, status } = data;

    const row = document.querySelector(`[data-pdf-id="${id}"]`);

    if (!row) {
      console.warn("no row found for pdf: ", id);
      return;
    }

    const statusEl = row.querySelector(".status");
    const spinnerEl = row.querySelector(".spinner");
    if (!statusEl || !spinnerEl) return;

    statusEl.textContent = status;

    let statusStyle = "";

    if (status.toLowerCase() === "ready") {
      statusStyle = "status bg-green-100 text-green-700 ";
      spinnerEl.className = "hidden spinner";
    }
    if (status.toLowerCase() === "uploaded") {
      statusStyle = "status bg-pink-100 text-pink-800";
    } else if (status.toLowerCase() === "failed") {
      statusStyle = "status bg-red-200 text-red-800 ";
      spinnerEl.className = "hidden spinner";
    } else if (status.toLowerCase() === "need_ocr")
      statusStyle = "status bg-orange-200 text-orange-800 flex";
    else if (status.toLowerCase() === "processing")
      statusStyle = "status bg-yellow-200 text-yellow-800 flex";
    else if (status.toLowerCase() === "embedding")
      statusStyle = "status bg-blue-200 text-blue-800 flex";

    statusEl.className = statusStyle;
  }
}

async function fetchPDFs() {
  console.log("fetching all user pdfS");
  // table body
  const tbodyEl = document.getElementById("pdfTableBody");
  const loadingEl = document.getElementById("pdf-loading");

  // set loading state
  loadingEl.classList.remove("hidden");
  tbodyEl.innerHTML = "";

  try {
    // request
    const data = await api.fetchPDFs();

    // success

    // hide loading
    loadingEl.classList.add("hidden");

    // console.log(data);

    // render pdfs table data
    data?.forEach((pdf) => {
      // create a row element
      const row = document.createElement("tr");
      row.className = "border-b hover:bg-gray-100 transition";
      // set data attribute
      row.dataset.pdfId = pdf._id;

      let statusStyle = "";
      let isInProcess = true;

      if (pdf.status.toLowerCase() === "ready") {
        statusStyle = "bg-green-100 text-green-700";
        isInProcess = false;
      } else if (pdf.status.toLowerCase() === "uploaded") {
        statusStyle = "bg-pink-100 text-pink-700";
      } else if (pdf.status.toLowerCase() === "failed") {
        statusStyle = "bg-red-200 text-red-800";
        isInProcess = false;
      } else if (pdf.status.toLowerCase() === "need_ocr")
        statusStyle = "bg-orange-200 text-orange-800";
      else if (pdf.status.toLowerCase() === "processing")
        statusStyle = "bg-yellow-200 text-yellow-800";
      else if (pdf.status.toLowerCase() === "embedding")
        statusStyle = "bg-blue-200 text-blue-800";

      row.innerHTML = `
        <td class="py-2 font-mono text-sm text-gray-700">${pdf._id}</td>
        <td class="py-2 text-gray-800">${pdf.filename}</td>
        <td class="py-2 flex gap-2">
          <span 
            class="
            status px-2 py-1 text-xs rounded-lg font-semibold 
            ${statusStyle}            
          ">
            ${pdf.status}
          </span>
          <div role="status" class="${isInProcess ? "flex" : "hidden"} spinner">
              <svg aria-hidden="true" class="inline w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-pink-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/>
                  <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/>
              </svg>
              <span class="sr-only">Loading...</span>
          </div>
        </td>

        <td class="py-2 text-gray-800">
          <button 
          class="downloadBtn bg-blue-300 hover:bg-blue-400 transition p-2 rounded-md"
          >
            download
          </button>
        </td>

        <td class="py-2 text-gray-800">
          <button 
          class="deleteBtn bg-red-300 hover:bg-red-400 transition p-2 rounded-md"
          >
            delete🗑
          </button>
        </td>
      `;

      // render each row into table body
      tbodyEl.appendChild(row);

      // attach click handler
      const btn = row.querySelector(".downloadBtn");
      btn.addEventListener("click", function () {
        handleDownload(pdf._id, this);
      });

      // set eventListener on delete button
      const deleteBtn = row.querySelector(".deleteBtn");
      deleteBtn.addEventListener("click", function () {
        handleDelete(pdf._id, this);
      });
    });
  } catch (err) {
    console.log(err);
    // set error
    loadingEl.textContent = "error loading PDFs.";
  }
}

async function handleDownload(pdf_id, btn) {
  // console.log(pdf_id, btn);
  const originalText = btn.textContent; // block-scoped

  try {
    // set loading state
    btn.textContent = "Loading...";
    btn.disabled = true;

    const data = await api.downloadPDF(pdf_id);

    // console.log(data);
  } catch (err) {
    console.error(err);
    window.alert("something went wrong while downloading PDF");
  } finally {
    // reset button
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

// delete pdf
async function handleDelete(pdf_id, btn) {
  const originalText = btn.textContent;

  if (!window.confirm("are you sure you want to delete this PDF?")) return;

  try {
    btn.textContent = "deleting..";
    btn.disabled = true;

    const data = await api.deletePDF(pdf_id);

    // remove from table
    const row = btn.closest("tr");
    row.remove();
  } catch (err) {
    console.error("error deleting PDF", err);
    window.alert("error deleting PDF");
  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

export { fetchPDFs, initPdfEvents };
