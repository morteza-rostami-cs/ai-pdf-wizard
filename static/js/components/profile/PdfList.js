const { defineComponent, ref, computed } = Vue;
const { RouterLink, useRouter } = VueRouter;
import { userStore } from "../../stores/userStore.js";

export default defineComponent({
  name: "PdfList",
  // components: { AuthGuard, GuestGuard },
  setup: () => {
    const router = useRouter();
    const loading = ref(false);

    return { userStore };
  },
  template: /*jsx*/ `
    <div>
      pdf list 
    </div>
  `,
});
