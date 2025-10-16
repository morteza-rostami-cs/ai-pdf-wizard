const { defineComponent, ref } = Vue;
const { useRouter } = VueRouter;
import { apiClient } from "../utils/api.js";
import { userStore } from "../stores/userStore.js";

export default defineComponent({
  name: "LogoutButton",
  setup() {
    const router = useRouter();
    const loading = ref(false);
    const showConfirm = ref(false);

    const logout = async () => {
      loading.value = true;
      try {
        await apiClient("/users/logout", "POST");
        userStore.user = null;
        router.push("/login");
      } catch (err) {
        console.error("Logout failed", err);
      } finally {
        loading.value = false;
        showConfirm.value = false;
      }
    };

    return { showConfirm, logout, loading };
  },
  template: /*html*/ `
    <div style="display:inline;">
      <!-- Logout Button -->
      <el-button type="danger" :loading="loading" @click="showConfirm = true">
        <span v-if="!loading">Logout</span>
      </el-button>

      <!-- Confirm Dialog -->
      <teleport to="body">
      <el-dialog
        v-model="showConfirm"
        title="Confirm Logout"
        width="300px"
      >
        <span>Are you sure you want to logout?</span>
        <template #footer>
          <el-button @click="showConfirm = false">No</el-button>
          <el-button type="primary" @click="logout">Yes</el-button>
        </template>
      </el-dialog>
      </teleport>
    </div>
  `,
});
