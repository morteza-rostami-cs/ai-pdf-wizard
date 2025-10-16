const { defineComponent, reactive, ref } = Vue;
import { apiClient } from "../utils/api.js";
const { useRouter } = VueRouter;

export default defineComponent({
  name: "RegisterPage",

  setup() {
    const router = useRouter();

    // form state
    const form = reactive({
      email: "",
    });

    // register loading state
    const loading = ref(false);

    // form client errors
    const errors = reactive({ email: "" });

    // client side form validation
    function validate() {
      errors.email = "";

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if (!form.email) errors.email = "Email is required";
      else if (!emailRegex.test(form.email)) {
        errors.email = "Invalid email";
      }

      return !errors.email; // return true if no errors
    }

    // submit register form
    async function submitForm() {
      // validate form
      if (!validate()) return;

      // set loading state
      loading.value = true;

      try {
        const data = await apiClient("/users/register", "POST", {
          email: form.email,
        });

        console.log(data);

        // toast
        Swal.fire({
          toast: true,
          position: "top-end",
          icon: "success",
          title: "OTP sent! Check your email.",
          showConfirmButton: false,
          timer: 3000,
        });

        // navigate to login page
        router.push("/login");
      } catch (error) {
        console.error(error);
        Swal.fire({
          toast: true,
          position: "top-end",
          icon: "error",
          title: error?.message || "OTP sent! Check your email.",
          showConfirmButton: false,
          timer: 3000,
        });
      } finally {
        loading.value = false; // set loading state
      }
    }

    return { form, errors, loading, submitForm };
  },

  template: `
    <el-card class="max-w-md mx-auto mt-20 p-8 shadow-md">
      <h2 class="text-2xl font-bold mb-6 text-center text-gray-900">
        Register
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
          />
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
            <template v-if="!loading">Register</template>
            <template v-else>Sending...</template>
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  `,
});
