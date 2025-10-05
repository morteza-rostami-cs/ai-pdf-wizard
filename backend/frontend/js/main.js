import { fetchAuthUser, showIfAuth, showIfGuest } from "./auth/auth.js";

// load auth user from backend, set promise on window
document.addEventListener("DOMContentLoaded", () => {
  console.log("fetching auth_user------");
  window.currentUserPromise = fetchAuthUser();
});
