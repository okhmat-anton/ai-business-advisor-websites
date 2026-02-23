// Authentication store - manages token from parent project
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const userId = ref<string>('user-1') // Mock user ID
  const userName = ref<string>('Demo User')
  const isLoading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value)

  // Actions

  /**
   * Initialize auth from URL params or localStorage
   * In production, token comes from parent project via ?token= or postMessage
   */
  function initAuth() {
    const urlParams = new URLSearchParams(window.location.search)
    const urlToken = urlParams.get('token')
    if (urlToken) {
      token.value = urlToken
      localStorage.setItem('auth_token', urlToken)
    }

    // Mock: auto-login for development
    if (!token.value) {
      token.value = 'mock-jwt-token-for-development'
      localStorage.setItem('auth_token', token.value)
    }
  }

  /**
   * Validate session against parent project API
   */
  async function validateSession(): Promise<boolean> {
    isLoading.value = true
    try {
      // Mock: always valid in dev mode
      await new Promise((resolve) => setTimeout(resolve, 200))
      isLoading.value = false
      return true
    } catch {
      token.value = null
      localStorage.removeItem('auth_token')
      isLoading.value = false
      return false
    }
  }

  function logout() {
    token.value = null
    userId.value = ''
    localStorage.removeItem('auth_token')
  }

  return {
    token,
    userId,
    userName,
    isLoading,
    isAuthenticated,
    initAuth,
    validateSession,
    logout,
  }
})
