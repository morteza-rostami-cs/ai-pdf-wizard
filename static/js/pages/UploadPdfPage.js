const {
  defineComponent,
  createApp,
  onMounted,
  onBeforeMount,
  watch,
  toRaw,
  ref,
} = Vue;

import PdfUploadForm from "../components/upload_pdf/PdfUploadForm.js";
import PdfList from "../components/upload_pdf/PdfList.js";

export default defineComponent({
  name: "UploadPdfPage",
  components: { PdfUploadForm, PdfList },
  template: /*html*/ `
    <div class="max-w-[600px] mx-auto p-4 mt-8">
      <PdfUploadForm />
      <PdfList />
    </div>
  `,
});
