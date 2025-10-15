const { defineComponent } = Vue;
import { userStore } from "../stores/userStore.js";

export default defineComponent({
  name: "HomePage",
  setup: () => {
    return { user: userStore.user };
  },
  template: `
    <div class="text-center">
      <h1 class="text-3xl font-bold mb-3">
        Welcome to AI PDF Wizard 📄✨
      </h1>
      <p class="text-gray-600">
        Upload PDFs and let AI help you understand them.
      </p>
    </div>
  `,
});
