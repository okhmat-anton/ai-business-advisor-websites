// UI store - manages panels, preview mode, and other UI state
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DevicePreviewMode } from '@/types/editor'

export const useUiStore = defineStore('ui', () => {
  // State
  const showSettingsPanel = ref(false)
  const showContentPanel = ref(false)
  const showBlocksLibrary = ref(false)
  const showSiteSettings = ref(false)
  const showPageSettings = ref(false)
  const showPageList = ref(false)
  const devicePreview = ref<string>('desktop')
  const insertAfterBlockId = ref<string | null>(null)

  // Actions
  function openSettingsPanel() {
    showSettingsPanel.value = true
    showContentPanel.value = false
  }

  function closeSettingsPanel() {
    showSettingsPanel.value = false
  }

  function openContentPanel() {
    showContentPanel.value = true
    showSettingsPanel.value = false
  }

  function closeContentPanel() {
    showContentPanel.value = false
  }

  function closeAllPanels() {
    showSettingsPanel.value = false
    showContentPanel.value = false
    showSiteSettings.value = false
    showPageSettings.value = false
    showPageList.value = false
  }

  function openBlocksLibrary(afterBlockId?: string) {
    insertAfterBlockId.value = afterBlockId || null
    showBlocksLibrary.value = true
  }

  function closeBlocksLibrary() {
    showBlocksLibrary.value = false
    insertAfterBlockId.value = null
  }

  function openPageSettings() {
    showPageSettings.value = true
  }

  function closePageSettings() {
    showPageSettings.value = false
  }

  function closeSiteSettings() {
    showSiteSettings.value = false
  }

  function closePageList() {
    showPageList.value = false
  }

  function setDevicePreview(mode: string) {
    devicePreview.value = mode
  }

  function togglePageList() {
    showPageList.value = !showPageList.value
  }

  function toggleSiteSettings() {
    showSiteSettings.value = !showSiteSettings.value
    if (showSiteSettings.value) showPageSettings.value = false
  }

  function togglePageSettings() {
    showPageSettings.value = !showPageSettings.value
    if (showPageSettings.value) showSiteSettings.value = false
  }

  return {
    showSettingsPanel,
    showContentPanel,
    showBlocksLibrary,
    showSiteSettings,
    showPageSettings,
    showPageList,
    devicePreview,
    insertAfterBlockId,
    openSettingsPanel,
    closeSettingsPanel,
    openContentPanel,
    closeContentPanel,
    closeAllPanels,
    openBlocksLibrary,
    closeBlocksLibrary,
    openPageSettings,
    closePageSettings,
    closeSiteSettings,
    closePageList,
    setDevicePreview,
    togglePageList,
    toggleSiteSettings,
    togglePageSettings,
  }
})
