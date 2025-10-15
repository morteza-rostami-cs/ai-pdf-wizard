const { defineComponent, computed } = Vue;
import { userStore } from "../stores/userStore.js";

export const AuthGuard = defineComponent({
  name: "AuthGuard",
  setup(_, { slots }) {
    const isAuth = computed(() => !userStore.loading && !!userStore.user);
    return () => (isAuth.value ? slots.default() : null);
  },
});
