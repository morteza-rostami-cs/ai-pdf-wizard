const { defineComponent, ref, computed } = Vue;
const { RouterLink, useRouter } = VueRouter;
import { userStore } from "../../stores/userStore.js";

export default defineComponent({
  name: "UploadForm",
  // components: { AuthGuard, GuestGuard },
  setup: () => {
    const router = useRouter();
    const loading = ref(false);

    return {};
  },
  template: /*jsx*/ `
    <div>
    upload pdf form
    </div>
  `,
});
