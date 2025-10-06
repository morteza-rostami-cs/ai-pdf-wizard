import { api } from "./api.js";

export async function fetchPDFs() {
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

      row.innerHTML = `
        <td class="py-2 font-mono text-sm text-gray-700">${pdf._id}</td>
        <td class="py-2 text-gray-800">${pdf.filename}</td>
        <td class="py-2">
          <span class="px-2 py-1 text-xs rounded-lg font-semibold ${
            pdf.status.toLowerCase() === "ready"
              ? "bg-green-100 text-green-700"
              : pdf.status.toLowerCase() === "uploaded"
              ? "bg-blue-100 text-blue-700"
              : "bg-yellow-100 text-yellow-700"
          }">
            ${pdf.status}
          </span>
        </td>
        <td class="py-2 text-gray-800">
          <button 
          class="downloadBtn bg-blue-300 hover:bg-blue-400 transition p-2 rounded-md"
          >
            download
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
