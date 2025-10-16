const { defineComponent } = Vue;
import { userStore } from "../stores/userStore.js";
import Profile from "../components/profile/Profile.js";
import UploadForm from "../components/profile/UploadForm.js";
import PdfList from "../components/profile/PdfList.js";

export default defineComponent({
  name: "ProfilePage",
  components: { Profile, UploadForm },
  setup() {
    return { userStore };
  },
  template: /*jsx*/ `
    <div class="text-center flex flex-col gap-4">
      sds
    </div>
  `,
});
