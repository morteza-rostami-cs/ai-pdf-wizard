import Header from "./components/Header.js";
import HomePage from "./pages/HomePage.js";
import RegisterPage from "./pages/RegisterPage.js";
import LoginPage from "./pages/LoginPage.js";
import ProfilePage from "./pages/ProfilePage.js";
// global user
import { userStore } from "./stores/userStore.js";
import { apiClient } from "./utils/api.js";

const { createApp, onMounted, onBeforeMount } = Vue;
const { createRouter, createWebHashHistory } = VueRouter;

//define routes
const routes = [
  { path: "/", component: HomePage },
  { path: "/register", component: RegisterPage, meta: { guestOnly: true } },
  { path: "/login", component: LoginPage, meta: { guestOnly: true } },
  { path: "/profile", component: ProfilePage, meta: { requiresAuth: true } },
];

// create router
const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// fetch auth_user
let pendingFetch = null;

export async function fetchAuthUser() {
  // if a fetch is already in progress, wait for it
  if (pendingFetch) return pendingFetch;

  pendingFetch = (async () => {
    userStore.loading = true;
    try {
      const data = await apiClient("/users/me", "POST");
      userStore.user = data?.authenticated ? data.user : null;
    } catch (err) {
      userStore.user = null;
    } finally {
      userStore.loading = false;
      pendingFetch = null;
    }
    return userStore.user;
  })();

  return pendingFetch;
}

// route guard to protected pages

router.beforeEach(async (to, from, next) => {
  // fetch auth user on each redirect
  await fetchAuthUser();

  // if auth-only
  if (to.meta.requiresAuth && !userStore.user) return next("/login");

  // guest-only
  if (to.meta.guestOnly && userStore.user) return next("/profile");

  // otherwise
  next();
});

// main app
const App = {
  components: { Header },

  setup() {
    // onMounted -> runs after Header render
    onBeforeMount(async () => {
      await fetchAuthUser();
    });
  },

  template: `
    <Header/>
    <div class="p-4">
      <router-view></router-view>
    </div>
  `,
};

createApp(App).use(router).mount("#app");
