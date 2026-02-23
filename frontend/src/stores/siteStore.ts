// Site store - manages current site data, pages, and global settings
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ISite, IPage, ISiteGlobalSettings } from '@/types/site'
import { fetchSites, fetchSite, createSite, updateSite, deleteSite, createPage, deletePage, updatePage, publishSite } from '@/api/mock'
import { slugify } from '@/utils/helpers'

export const useSiteStore = defineStore('site', () => {
  // State
  const sites = ref<ISite[]>([])
  const currentSite = ref<ISite | null>(null)
  const currentPage = ref<IPage | null>(null)
  const isLoading = ref(false)

  // Getters
  const currentPages = computed(() => currentSite.value?.pages || [])
  const siteCount = computed(() => sites.value.length)

  // Actions

  /** Load all sites for current user */
  async function loadSites() {
    isLoading.value = true
    try {
      sites.value = await fetchSites()
    } finally {
      isLoading.value = false
    }
  }

  /** Load a specific site */
  async function loadSite(siteId: string) {
    isLoading.value = true
    try {
      currentSite.value = await fetchSite(siteId)
      if (currentSite.value?.pages.length) {
        currentPage.value = currentSite.value.pages.find((p: IPage) => p.isMain) ?? currentSite.value.pages[0] ?? null
      }
    } finally {
      isLoading.value = false
    }
  }

  /** Create a new site */
  async function addSite(name: string, description?: string) {
    const site = await createSite(name, description)
    sites.value.push(site)
    return site
  }

  /** Update current site */
  async function saveSite(data: Partial<ISite>) {
    if (!currentSite.value) return
    const updated = await updateSite(currentSite.value.id, data)
    if (updated) {
      currentSite.value = updated
      const idx = sites.value.findIndex((s: ISite) => s.id === updated.id)
      if (idx !== -1) sites.value[idx] = updated
    }
  }

  /** Delete a site */
  async function removeSite(siteId: string) {
    const success = await deleteSite(siteId)
    if (success) {
      sites.value = sites.value.filter((s: ISite) => s.id !== siteId)
      if (currentSite.value?.id === siteId) {
        currentSite.value = null
        currentPage.value = null
      }
    }
  }

  /** Update global settings */
  async function updateGlobalSettings(settings: Partial<ISiteGlobalSettings>) {
    if (!currentSite.value) return
    currentSite.value.globalSettings = { ...currentSite.value.globalSettings, ...settings }
    await saveSite({ globalSettings: currentSite.value.globalSettings })
  }

  /** Add a new page to current site */
  async function addPage(siteId: string, title: string) {
    if (!currentSite.value) return null
    const slug = slugify(title)
    const page = await createPage(siteId, title, slug)
    if (page) {
      currentSite.value.pages.push(page)
    }
    return page
  }

  /** Remove a page */
  async function removePage(siteId: string, pageId: string) {
    if (!currentSite.value) return
    const success = await deletePage(siteId, pageId)
    if (success) {
      currentSite.value.pages = currentSite.value.pages.filter((p: IPage) => p.id !== pageId)
      if (currentPage.value?.id === pageId) {
        currentPage.value = currentSite.value.pages[0] || null
      }
    }
  }

  /** Update a page */
  async function savePage(siteId: string, data: IPage) {
    if (!currentSite.value) return
    const updated = await updatePage(siteId, data.id, data)
    if (updated) {
      const idx = currentSite.value.pages.findIndex((p: IPage) => p.id === data.id)
      if (idx !== -1) currentSite.value.pages[idx] = updated
      if (currentPage.value?.id === data.id) currentPage.value = updated
    }
  }

  /** Set current page for editing */
  function setCurrentPage(pageId: string) {
    if (!currentSite.value) return
    currentPage.value = currentSite.value.pages.find((p: IPage) => p.id === pageId) || null
  }

  /** Publish the entire site */
  async function publish() {
    if (!currentSite.value) return
    const success = await publishSite(currentSite.value.id)
    if (success) {
      currentSite.value.status = 'published'
      currentSite.value.pages.forEach((p: IPage) => (p.status = 'published'))
    }
    return success
  }

  return {
    sites,
    currentSite,
    currentPage,
    isLoading,
    currentPages,
    siteCount,
    loadSites,
    loadSite,
    addSite,
    saveSite,
    removeSite,
    updateGlobalSettings,
    addPage,
    removePage,
    savePage,
    setCurrentPage,
    publish,
  }
})
