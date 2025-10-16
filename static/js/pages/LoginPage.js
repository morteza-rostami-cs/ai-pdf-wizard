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

  template: /*jsx*/ `
    <el-card class="max-w-md mx-auto mt-20 p-8 shadow-md">
      <h2 class="text-2xl font-bold mb-6 text-center text-gray-900">
        Login
      </h2>

      <el-form label-position="top" @submit.prevent class="flex flex-col gap-4">
        <!-- Email -->
        <el-form-item
          label="Email"
          :error="errors.email"
        >
          <el-input
            v-model="form.email"
            type="email"
            placeholder="name@example.com"
            clearable
          />
        </el-form-item>

        <!-- OTP -->
        <el-form-item
          label="OTP Code"
          :error="errors.otp"
        >
          <el-input
            v-model="form.otp"
            type="text"
            placeholder="Enter your OTP code"
            maxlength="6"
            clearable
          >
            <template #append>
              <el-icon><i class="el-icon-key"></i></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- Submit -->
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            :disabled="loading"
            class="w-full"
            @click="submitForm"
          >
            <template v-if="!loading">Login</template>
            <template v-else>Logging in...</template>
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  `,
});
