import { showIfAuth, showIfGuest, attachLogoutButton } from "./auth/auth.js";

// loading header
export async function loadHeader() {
  const res = await fetch("./partials/header.html");

  // insert into doc
  document.getElementById("header").innerHTML = await res.text();

  showIfAuth("logout-btn"); // auth
  showIfGuest("register-btn", "login-btn"); // guest

  // logout button logic
  attachLogoutButton();
}
