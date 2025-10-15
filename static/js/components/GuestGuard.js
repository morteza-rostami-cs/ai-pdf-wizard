const { defineComponent, computed } = Vue;
import { userStore } from "../stores/userStore.js";

export const GuestGuard = defineComponent({
  name: "GuestGuard",
  setup(_, { slots }) {
    const isGuest = computed(() => !userStore.loading && !userStore.user);
    return () => (isGuest.value ? slots.default() : null);
  },
});
