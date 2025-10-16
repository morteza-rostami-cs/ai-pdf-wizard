const {
  defineComponent,
  createApp,
  onMounted,
  onBeforeMount,
  watch,
  toRaw,
  ref,
} = Vue;
const { UploadFilled } = ElementPlusIconsVue;

import { apiClient } from "../../utils/api.js";

export default defineComponent({
  name: "PdfUploadForm",
  components: {
    "el-upload": ElementPlus.ElUpload,
    "el-button": ElementPlus.ElButton,
    "el-message": ElementPlus.ElMessage,
    "el-icon": ElementPlus.ElIcon,
    "upload-filled": UploadFilled,
  },
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
  template: /*html*/ `
    <div class="mb-4 bg-slate-100 rounded-md shadow-md p-4">
  
      
      <p v-if="message">{{ message }}</p>

      <el-upload
        class="upload-demo"
        drag
        
        multiple
        :before-upload="beforeUpload"
        :on-change="handleChange"
        :on-success="handleSuccess"
        :on-error="handleError"
      >
        <el-icon class="el-icon--upload">
          <upload-filled />
        </el-icon>
        <div class="el-upload__text">
          Drop PDF here or <em>click to upload</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            PDF files only
          </div>
        </template>
      </el-upload>

      <el-button type="primary" :loading="loading" @click="uploadPdf">Upload PDF</el-button>
    </div>
  `,
});
