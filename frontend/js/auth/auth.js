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
    console.log(data);
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
