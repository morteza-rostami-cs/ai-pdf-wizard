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
  name: "PdfUploadForm",
  setup() {
    const file = ref(null);
    const loading = ref(false);
    const message = ref("");

    const handleFileChange = (e) => {
      file.value = e.target.files[0];
    };

    const uploadPdf = async () => {
      if (!file.value) return;
      loading.value = true;
      message.value = "";
      const formData = new FormData();
      formData.append("pdf", file.value);

      try {
        await apiClient("/pdf/upload", "POST", formData);
        message.value = "Upload successful!";
        file.value = null;
        // optionally emit an event to PdfList to refresh
      } catch (err) {
        console.error(err);
        message.value = "Upload failed!";
      } finally {
        loading.value = false;
      }
    };

    return { file, loading, message, handleFileChange, uploadPdf };
  },
  template: `
    <div class="mb-4">
      <input type="file" accept="application/pdf" @change="handleFileChange" />
      <el-button type="primary" :loading="loading" @click="uploadPdf">Upload PDF</el-button>
      <p v-if="message">{{ message }}</p>
    </div>
  `,
});
