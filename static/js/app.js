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

// route guard to protected pages

router.beforeEach((to, from, next) => {
  console.log("redirecting to route, ", to);
  if (userStore.loading) {
    // request to /users/me is pending
    const stop = setInterval(() => {
      if (!userStore.loading) {
        clearInterval(stop);
        handleGuards(to, next);
      }
    }, 50);
  } else {
    // request to /me is done -> whether we have the user or not
    handleGuards(to, next);
  }
});

function handleGuards(to, next) {
  // if auth-only
  if (to.meta.requiresAuth && !userStore.user) return next("/login");

  // guest-only
  if (to.meta.guestOnly && userStore.user) return next("/profile");

  // otherwise
  next();
}

// main app
const App = {
  components: { Header },

  setup() {
    // onMounted -> runs after Header render
    onBeforeMount(async () => {
      console.log("start App component");
      // if user not loaded
      if (!userStore.user && !userStore.loading) {
        userStore.loading = true;
        try {
          // fetch auth user
          const data = await apiClient("/users/me", "POST");
          userStore.user = data?.authenticated ? data.user : null;

          console.log(userStore.user);
        } catch (err) {
          console.error("failed to fetch /me ", err);
          userStore.user = null;
        } finally {
          userStore.loading = false;
        }
      }
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
