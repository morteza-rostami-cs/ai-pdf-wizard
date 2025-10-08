import { fetchAuthUser } from "./auth.js";

// automatically refresh auth state on page load

export function authGuard() {
  console.log("🥩");

  window.currentUserPromise.then((data) => {
    const user = data.user;
    console.log("🥩");
    if (!user) {
      window.location.href = "/login.html";
      return;
    }

    // do not show a flash of ui
    document.body.style.visibility = "visible";
  });
}
