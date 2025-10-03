import { api } from "../api.js";

// global state
window.Auth = { user: null };

export async function fetchAuthUser() {
  try {
    const data = await api.get_me();

    if (data.authenticated) {
      window.Auth.user = data.user;
    } else {
      window.Auth.user = null;
    }

    return data;
  } catch (err) {
    console.error("error fetching user: ", err);
    // reset global
    window.Auth.user = null;
    return null;
  }
}

// show elements only to auth user
export function showIfAuth(...ids) {
  window.currentUserPromise.then((data) => {
    // const user = data.user;
    if (data.authenticated) {
      ids.forEach((id) => {
        const el = document.getElementById(id);

        if (el) el.classList.remove("hidden");
      });
    }
  });
}

// show elements only if user is not authenticated
export function showIfGuest(...ids) {
  window.currentUserPromise.then((data) => {
    if (!data.authenticated) {
      ids.forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.classList.remove("hidden");
      });
    }
  });
}

export async function logout() {
  try {
    await api.logout();

    // on logout success

    // clear global state
    window.Auth.user = null;

    // redirect to login
    window.location.href = "/frontend/login.html";
  } catch (err) {
    console.error("logout request failed: ", err);
  }
}

// setup event listener on logout button
export function attachLogoutButton(buttonId = "logout-btn") {
  const btn = document.getElementById(buttonId);

  if (btn) {
    btn.addEventListener("click", logout);
  }
}

export function getAuthData(func = (data) => {}) {
  document.addEventListener("DOMContentLoaded", () => {
    window.currentUserPromise.then((data) => {
      func(data.user);
    });
  });
}
