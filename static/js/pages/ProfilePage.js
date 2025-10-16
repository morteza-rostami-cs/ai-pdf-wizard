const { defineComponent } = Vue;
import { userStore } from "../stores/userStore.js";
import Profile from "../components/profile/Profile.js";

export default defineComponent({
  name: "ProfilePage",
  //components: { Profile, UploadForm },
  setup() {
    return { userStore };
  },
  template: /*html*/ `
    <div class="text-center flex flex-col gap-4">
      sds
    </div>
  `,
});
