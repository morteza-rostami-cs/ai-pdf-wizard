const {
  defineComponent,
  createApp,
  onMounted,
  onBeforeMount,
  watch,
  toRaw,
  ref,
} = Vue;

import { apiClient } from "../../utils/api.js";

export default defineComponent({
  name: "PdfList",
  setup() {
    const pdfs = ref([]);

    const fetchPdfs = async () => {
      try {
        pdfs.value = await apiClient("/pdfs/my-pdfs", "GET");
      } catch (err) {
        console.error(err);
      }
    };

    onMounted(fetchPdfs);

    return { pdfs, fetchPdfs };
  },
  template: `
    <div>
      <h3>Uploaded PDFs</h3>
      <ul>
        <li v-for="pdf in pdfs" :key="pdf.id">
          <a :href="pdf.url" target="_blank">{{ pdf.name }}</a>
        </li>
      </ul>
    </div>
  `,
});
