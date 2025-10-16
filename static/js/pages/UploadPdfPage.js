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
    <div>
      <PdfUploadForm />
      <PdfList />
    </div>
  `,
});
