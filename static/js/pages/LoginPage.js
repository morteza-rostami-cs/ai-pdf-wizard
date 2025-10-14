const { defineComponent, reactive, ref } = Vue;
import { apiClient } from "../utils/api.js";
const { useRouter } = VueRouter;

export default defineComponent({
  name: "LoginPage",

  setup() {
    const router = useRouter();

    // form state
    const form = reactive({
      email: "",
      otp: "",
    });

    // register loading state
    const loading = ref(false);

    // form client errors
    const errors = reactive({ email: "", otp: "" });

    // client side form validation
    function validate() {
      errors.email = "";
      errors.otp = "";

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if (!form.email) errors.email = "Email is required";
      else if (!emailRegex.test(form.email)) {
        errors.email = "Invalid email";
      }

      // validate otp
      if (!form.otp) errors.otp = "OTP is required";
      else if (form.otp.length < 4)
        errors.otp = "OTP must be at least 4 digits";

      return !errors.email && !errors.otp;
    }

    // submit register form
    async function submitForm() {
      // validate form
      if (!validate()) return;

      // set loading state
      loading.value = true;

      try {
        const data = await apiClient("/users/login", "POST", {
          email: form.email,
          otp_code: form.otp,
        });

        console.log(data);

        // toast
        Swal.fire({
          toast: true,
          position: "top-end",
          icon: "success",
          title: "You are logged in.",
          showConfirmButton: false,
          timer: 3000,
        });

        // navigate to login page
        router.push("/profile");
      } catch (error) {
        console.error(error);
        Swal.fire({
          toast: true,
          position: "top-end",
          icon: "error",
          title: error?.message || "login has failed.",
          showConfirmButton: false,
          timer: 3000,
        });

        // router.push("/profile");
      } finally {
        loading.value = false; // set loading state
      }
    }

    return { form, errors, loading, submitForm };
  },

  template: `
    <form 
      @submit.prevent="submitForm" 
      class="max-w-sm mx-auto mt-12 p-6 bg-white border border-gray-200 rounded-lg shadow-md">
      
      <h2 class="text-2xl font-bold mb-6 text-gray-900">Login</h2>

      <!-- Email -->
      <div class="mb-5">
        <label for="email" class="block mb-2 text-sm font-medium text-gray-900">Email</label>
        <input
          type="email"
          id="email"
          v-model="form.email"
          placeholder="name@example.com"
          class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg 
          focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        />
        <p v-if="errors.email" class="text-red-500 text-sm mt-1">
          {{ errors.email }}
        </p>
      </div>

      <!-- OTP -->
      <div class="mb-5">
        <label for="otp" class="block mb-2 text-sm font-medium text-gray-900">OTP Code</label>
        <input
          type="text"
          id="otp"
          v-model="form.otp"
          placeholder="Enter your OTP code"
          class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg 
          focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        />
        <p v-if="errors.otp" class="text-red-500 text-sm mt-1">
          {{ errors.otp }}
        </p>
      </div>

      <!-- Submit -->
      <button
        type="submit"
        class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 
        focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm 
        w-full px-5 py-2.5 text-center"
        :disabled="loading"
      >
        <span v-if="loading">Logging in...</span>
        <span v-else>Login</span>
      </button>
    </form>
  `,
});
