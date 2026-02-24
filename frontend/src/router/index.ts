import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@/pages/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/sites/:siteId',
    name: 'site-pages',
    component: () => import('@/pages/SitePagesPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/editor/:siteId',
    name: 'editor-site',
    component: () => import('@/pages/EditorPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/editor/:siteId/:pageId',
    name: 'editor',
    component: () => import('@/pages/EditorPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/preview/:siteId/:pageId',
    name: 'preview',
    component: () => import('@/pages/PreviewPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    // Public page — no auth required
    path: '/site/:slug?',
    name: 'public',
    component: () => import('@/pages/PublicPage.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard: validate session once per app session
let sessionValidated = false

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) return true

  const authStore = useAuthStore()

  // If already validated this session, just check the stored result
  if (sessionValidated) {
    if (!authStore.isAuthenticated) {
      authStore.redirectToLogin()
      return false
    }
    return true
  }

  // First protected route visit — validate against external API
  const valid = await authStore.validateSession()
  sessionValidated = true

  if (!valid) {
    authStore.redirectToLogin()
    return false
  }

  return true
})

export default router

