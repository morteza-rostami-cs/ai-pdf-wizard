import { fetchAuthUser } from "./auth.js";

// automatically refresh auth state on page load
document.addEventListener("DOMContentLoaded", async () => {
  const data = await fetchAuthUser();

  const user = data.user;

  if (!user) {
    window.location.href = "/frontend/login.html";
    return;
  }

  // do not show a flash of ui
  document.body.style.visibility = "visible";
});
