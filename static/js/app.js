import Header from "./components/Header.js";
import HomePage from "./pages/HomePage.js";
import RegisterPage from "./pages/RegisterPage.js";
import LoginPage from "./pages/LoginPage.js";
import ProfilePage from "./pages/ProfilePage.js";

const { createApp } = Vue;
const { createRouter, createWebHashHistory } = VueRouter;

//define routes
const routes = [
  { path: "/", component: HomePage },
  { path: "/register", component: RegisterPage },
  { path: "/login", component: LoginPage },
  { path: "/profile", component: ProfilePage },
];

// create router
const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// main app
const App = {
  components: { Header },
  template: `
    <Header/>
    <div class="p-4">
      <router-view></router-view>
    </div>
  `,
};

// mount our app
createApp(App).use(router).mount("#app");
