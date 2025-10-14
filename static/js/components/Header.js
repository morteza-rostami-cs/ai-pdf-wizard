const { defineComponent } = Vue;
const { RouterLink } = VueRouter;

export default defineComponent({
  name: "Header",
  template: `
    <nav class="bg-indigo-600 text-white p-4 flex justify-between">
      <div class="font-bold text-lg">AI PDF Wizard</div>
      <div class="space-x-4">
        <RouterLink to="/" class="hover:text-yellow-300">
          Home
        </RouterLink>
        <RouterLink to="/register" class="hover:text-yellow-300">
          register
        </RouterLink>
        <RouterLink to="/login" class="hover:text-yellow-300">
          login
        </RouterLink>

        <RouterLink to="/profile" class="hover:text-yellow-300">
          profile
        </RouterLink>
      </div>
    </nav>
  `,
});
