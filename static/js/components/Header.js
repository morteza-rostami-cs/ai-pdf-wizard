const { defineComponent, ref, computed } = Vue;
const { RouterLink, useRouter } = VueRouter;
import { userStore } from "../stores/userStore.js";
import { apiClient } from "../utils/api.js";
import { AuthGuard } from "./AuthGuard.js";
import { GuestGuard } from "./GuestGuard.js";
import LogoutButton from "./LogoutButton.js";

export default defineComponent({
  name: "Header",
  components: { AuthGuard, GuestGuard, LogoutButton },
  setup: () => {
    const router = useRouter();
    const loading = ref(false);

    async function logout() {
      loading.value = true;
      try {
        await apiClient("/users/logout", "POST");
      } catch (err) {
        console.error("Logout failed", err);
      } finally {
        loading.value = false;
        userStore.user = null; // clear global user
        router.push("/login");
      }
    }

    return { logout, userStore, loading };
  },
  template: /*html*/ `
    <el-header height="60px" class="bg-indigo-600 text-white flex justify-between items-center px-6">
  
      <RouterLink to="/" class="text-xl font-bold text-white hover:text-yellow-300">
        AI PDF Wizard
      </RouterLink>

     
      <div class="flex items-center space-x-2">
       
        <GuestGuard>
          <RouterLink to="/register">
            <el-button text type="primary">Register</el-button>
          </RouterLink>
          <RouterLink to="/login">
            <el-button text type="primary">Login</el-button>
          </RouterLink>
        </GuestGuard>


        <AuthGuard>
          <RouterLink to="/upload-pdf">
            <el-button text type="primary">Upload PDF</el-button>
          </RouterLink>

          <el-dropdown trigger="click" @command="cmd => cmd === 'profile' ? router.push('/profile') : null">
            <span class="el-dropdown-link cursor-pointer flex items-center space-x-2">
              <el-avatar :size="28">{{ '' }}</el-avatar>
              <span class="text-white">{{ 'profile' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <RouterLink to="/profile">
                    <el-button text type="primary">
                    profile
                    </el-button>
                  </RouterLink>
                </el-dropdown-item>
                <el-dropdown-item divided>
                  <LogoutButton />
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </AuthGuard>
      </div>
    </el-header>
  `,
});
