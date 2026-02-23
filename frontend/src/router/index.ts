import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@/pages/DashboardPage.vue'),
  },
  {
    path: '/editor/:siteId',
    name: 'editor-site',
    component: () => import('@/pages/EditorPage.vue'),
  },
  {
    path: '/editor/:siteId/:pageId',
    name: 'editor',
    component: () => import('@/pages/EditorPage.vue'),
  },
  {
    path: '/preview/:siteId/:pageId',
    name: 'preview',
    component: () => import('@/pages/PreviewPage.vue'),
  },
  {
    path: '/site/:slug?',
    name: 'public',
    component: () => import('@/pages/PublicPage.vue'),
  },
  {
    // Catch-all 404
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
