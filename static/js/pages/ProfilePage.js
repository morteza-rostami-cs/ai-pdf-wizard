const { defineComponent } = Vue;
import { userStore } from "../stores/userStore.js";

export default defineComponent({
  name: "ProfilePage",
  setup() {
    return { userStore };
  },
  template: `
    <div class="text-center flex flex-col gap-4">
      <h1 class="text-3xl font-bold mb-3">
        profile page 📄✨
      </h1>
      <p class="text-gray-800">
        {{userStore?.user?.email}}
      </p>
    </div>
  `,
});
