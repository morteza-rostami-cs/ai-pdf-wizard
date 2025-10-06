import { fetchAuthUser } from "./auth.js";

// automatically refresh auth state on page load
export function guestGuard() {
  window.currentUserPromise.then((data) => {
    const user = data.user;

    if (user) {
      window.location.href = "/index.html";
      return;
    }

    // do not show a flash of ui
    document.body.style.visibility = "visible";
  });
}
