import { fetchAuthUser, showIfAuth, showIfGuest } from "./auth/auth.js";

// load auth user from backend, set promise on window
document.addEventListener("DOMContentLoaded", () => {
  window.currentUserPromise = fetchAuthUser();
});
