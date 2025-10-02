import { api } from "../api.js";

// grab some elements
const form = document.getElementById("loginForm");

const submitBtn = document.querySelector("#submitBtn");
// message div
const messageDiv = document.querySelector("#message");

// form handler
form.addEventListener("submit", async (e) => {
  console.log("*********start login form submit ***********");
  // stop default behavior
  e.preventDefault();

  const email = document.getElementById("email").value.trim();
  const otp_code = document.getElementById("otp").value.trim();

  // email exist
  if (!email) {
    console.log("Email can't be empty");
    return;
  }

  if (!otp_code) {
    console.log("otp code can't be empty");
    return;
  }

  // reset message and set button loading
  messageDiv.textContent = "";
  submitBtn.disabled = true;
  submitBtn.textContent = "Loading login...";

  try {
    // login request
    const data = await api.login({ email, otp_code: otp_code });

    // success message
    messageDiv.textContent = `login success, ${data?.user.id}`;
    messageDiv.className = "mt-4 text-center text-green-600";

    // redirect to /profile page
    window.location.href = "/frontend/profile.html";
  } catch (error) {
    // show error message
    messageDiv.textContent = error.message;
    messageDiv.className = "mt-4 text-center text-red-600";
  } finally {
    // reset button ui
    submitBtn.disabled = false;
    submitBtn.textContent = "login";
  }
});
