import { api } from "../api.js";

// grab some elements
const form = document.getElementById("registerForm");

const submitBtn = document.querySelector("#submitBtn");
// message div
const messageDiv = document.querySelector("#message");

// form handler
form.addEventListener("submit", async (e) => {
  console.log("*********start register form submit ***********");
  // stop default behavior
  e.preventDefault();

  const email = document.getElementById("email").value.trim();

  // email exist
  if (!email) {
    console.log("Email can't be empty");
    return;
  }

  // reset message and set button loading
  messageDiv.textContent = "";
  submitBtn.disabled = true;
  submitBtn.textContent = "Loading register...";

  try {
    // register request
    const data = await api.register({ email });

    // success message
    messageDiv.textContent = `register success, ${data.otp_code}`;
    messageDiv.className = "mt-4 text-center text-green-600";
  } catch (error) {
    // show error message
    messageDiv.textContent = error.message;
    messageDiv.className = "mt-4 text-center text-red-600";
  } finally {
    // reset button ui
    submitBtn.disabled = false;
    submitBtn.textContent = "Register";
  }
});
