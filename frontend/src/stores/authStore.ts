// Authentication store - validates JWT from parent project (app.akm-advisor.com)
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const EXTERNAL_LOGIN_URL = 'https://app.akm-advisor.com/auth/login'
const COOKIE_NAME = 'akm_auth_token'
const STORAGE_KEY = 'auth_token'

// --- Cookie helpers ---
function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'))
  return match ? decodeURIComponent(match[1] ?? '') : null
}

function setCookie(name: string, value: string, days = 7): void {
  const expires = new Date(Date.now() + days * 864e5).toUTCString()
  // Use parent domain so the cookie is shared between app.akm-advisor.com and builder.akm-advisor.com
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; domain=.akm-advisor.com; SameSite=Lax`
}

function deleteCookie(name: string): void {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=.akm-advisor.com`
}

export interface AuthUser {
  id: string
  email: string
  name: string
  company?: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<AuthUser | null>(null)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  /**
   * Resolve token priority: URL param → cookie → localStorage
   */
  function resolveToken(): string | null {
    // 1. URL param ?token=
    const params = new URLSearchParams(window.location.search)
    const urlToken = params.get('token')
    if (urlToken) {
      // Persist and strip from URL
      setCookie(COOKIE_NAME, urlToken)
      localStorage.setItem(STORAGE_KEY, urlToken)
      params.delete('token')
      const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '')
      window.history.replaceState({}, '', newUrl)
      return urlToken
    }

    // 2. Cookie (set by parent app on shared .akm-advisor.com domain)
    const cookieToken = getCookie(COOKIE_NAME)
    if (cookieToken) {
      localStorage.setItem(STORAGE_KEY, cookieToken)
      return cookieToken
    }

    // 3. localStorage fallback
    return localStorage.getItem(STORAGE_KEY)
  }

  /**
   * Validate token against our backend (which proxies to app.akm-advisor.com/api/v1/auth/me).
   * In mock mode (VITE_USE_MOCK=true) skips validation and returns a demo user.
   * Returns true if valid, false otherwise.
   */
  async function validateSession(): Promise<boolean> {
    // Mock mode — skip external validation
    if (import.meta.env.VITE_USE_MOCK !== 'false') {
      token.value = 'mock-token'
      user.value = { id: 'demo-user', email: 'demo@example.com', name: 'Demo User', company: 'Demo Co' }
      return true
    }

    isLoading.value = true
    try {
      const t = resolveToken()
      if (!t) return false

      const response = await axios.get(`https://app.akm-advisor.com/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${t}` },
        timeout: 10000,
      })

      token.value = t
      user.value = {
        id: String(response.data.id ?? response.data.user_id ?? ''),
        email: response.data.email ?? '',
        name: response.data.name ?? response.data.full_name ?? response.data.first_name ?? '',
        company: response.data.company ?? response.data.company_name ?? response.data.tenant_name ?? '',
      }
      // Keep localStorage in sync
      localStorage.setItem(STORAGE_KEY, t)
      return true
    } catch (error) {
      console.error('Session validation failed:', error)
      clearAuth()
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Redirect to parent project login, passing current URL as ?redirect=
   */
  function redirectToLogin(): void {
    const redirect = encodeURIComponent(window.location.href)
    window.location.href = `${EXTERNAL_LOGIN_URL}?redirect=${redirect}`
  }

  function clearAuth(): void {
    token.value = null
    user.value = null
    localStorage.removeItem(STORAGE_KEY)
    deleteCookie(COOKIE_NAME)
  }

  function logout(): void {
    clearAuth()
    redirectToLogin()
  }

  // Legacy compat
  const userId = computed(() => user.value?.id ?? '')
  const userName = computed(() => user.value?.name ?? '')

  return {
    token,
    user,
    userId,
    userName,
    isLoading,
    isAuthenticated,
    validateSession,
    redirectToLogin,
    logout,
  }
})

