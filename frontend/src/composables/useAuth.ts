// Auth composable - retrieves and validates token from parent project (app.akm-advisor.com)
import { useAuthStore } from '@/stores/authStore'

export function useAuth() {
  const authStore = useAuthStore()

  return {
    isAuthenticated: authStore.isAuthenticated,
    userId: authStore.userId,
    userName: authStore.userName,
    user: authStore.user,
    token: authStore.token,
    isLoading: authStore.isLoading,
    validateSession: authStore.validateSession,
    logout: authStore.logout,
  }
}
