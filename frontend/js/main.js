import { fetchAuthUser, showIfAuth, showIfGuest } from "./auth/auth.js";
import { loadHeader } from "./header.js";
import { authGuard } from "./auth/authGuard.js";
import { guestGuard } from "./auth/guestGuard.js";
import { initSocket } from "./sockets.js";

// load auth user from backend, set promise on window
document.addEventListener("DOMContentLoaded", () => {
  console.log("fetching auth_user------");

  // fetch auth user -> assign to global promise
  window.currentUserPromise = fetchAuthUser();

  // on auth
  window.currentUserPromise.then((data) => {
    const authenticated = data.authenticated;
    // start sse connection only for auth users
    // if (authenticated) connectSse();
    if (authenticated) initSocket();
  });

  // load header on every page
  loadHeader();

  const page = document.body.dataset.page;
  console.log(`current page: ${page}`);

  // add auth guard -> upload, profile
  if (["profile", "upload"].includes(page)) {
    authGuard();
  }

  if (["register", "login"].includes(page)) {
    guestGuard();
  }

  // page specific scripts
  switch (page) {
    case "profile":
      import("./pages/profile.js").then((m) => m.initProfilePage());
      break;

    case "register":
      import("./pages/register.js").then((m) => m.initRegisterPage());
      break;

    case "login":
      import("./pages/login.js").then((m) => m.initLoginPage());
      break;

    case "upload":
      import("./pages/uploadPage.js").then((m) => m.initUploadPage());
      break;
    case "index":
      import("./pages/index.js").then((m) => m.initIndexPage());
      break;
    default:
      console.log("no page module for: ", page);
  }
});
