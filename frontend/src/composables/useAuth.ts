// Auth composable - retrieves and validates token from parent project
import { useAuthStore } from '@/stores/authStore'
import { onMounted } from 'vue'

export function useAuth() {
  const authStore = useAuthStore()

  onMounted(() => {
    authStore.initAuth()
  })

  return {
    isAuthenticated: authStore.isAuthenticated,
    userId: authStore.userId,
    userName: authStore.userName,
    validateSession: authStore.validateSession,
    logout: authStore.logout,
  }
}
