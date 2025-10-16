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
  template: /*jsx*/ `
    <nav class="bg-indigo-600 text-white p-4 flex justify-between">
      <div class="font-bold text-lg">AI PDF Wizard</div>

      <div class="space-x-4">
        
        <RouterLink to="/" class="hover:text-yellow-300">
          Home
        </RouterLink>
        <GuestGuard>
          <RouterLink  to="/register" class="hover:text-yellow-300">
            register
          </RouterLink>
          <RouterLink  to="/login" class="hover:text-yellow-300">
            login
          </RouterLink>
        </GuestGuard>
      
        <AuthGuard>
          <RouterLink  to="/profile" class="hover:text-yellow-300">
            profile
          </RouterLink>
        
          <LogoutButton/>
          
        </AuthGuard>
      </div>
    </nav>
  `,
});
