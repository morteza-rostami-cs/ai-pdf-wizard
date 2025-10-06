import { getAuthData } from "../auth/auth.js";

/**
 * initiate profile page stuff
 * */
export function initProfilePage() {
  // get fresh user data
  getAuthData((user) => {
    console.log(user);
    const email = document.getElementById("email");
    const plan = document.getElementById("planType");

    email.textContent = user.email;
    plan.textContent = user.plan;
  });
}
