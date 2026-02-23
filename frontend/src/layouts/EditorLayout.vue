<template>
  <v-app>
    <!-- Editor Toolbar at top -->
    <EditorToolbar />

    <!-- Side panels -->
    <PageList />
    <SettingsPanel />
    <ContentPanel />

    <!-- Modals -->
    <BlocksLibraryModal />
    <SiteSettings />
    <PageSettings />

    <!-- Main content: editor canvas -->
    <v-main class="editor-main">
      <EditorCanvas />
    </v-main>

    <!-- Snackbar for notifications -->
    <v-snackbar
      v-model="showSnackbar"
      :color="snackbarColor"
      timeout="3000"
      location="bottom right"
    >
      {{ snackbarText }}
    </v-snackbar>
  </v-app>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useEditorStore } from '@/stores/editorStore'
import { useSiteStore } from '@/stores/siteStore'
import { useUndoRedo } from '@/composables/useUndoRedo'
import { useAutoSave } from '@/composables/useAutoSave'

// Editor components
import EditorToolbar from '@/components/editor/EditorToolbar.vue'
import EditorCanvas from '@/components/editor/EditorCanvas.vue'
import SettingsPanel from '@/components/editor/SettingsPanel.vue'
import ContentPanel from '@/components/editor/ContentPanel.vue'
import BlocksLibraryModal from '@/components/editor/BlocksLibraryModal.vue'

// Site components
import PageList from '@/components/site/PageList.vue'
import SiteSettings from '@/components/site/SiteSettings.vue'
import PageSettings from '@/components/site/PageSettings.vue'

const route = useRoute()
const editorStore = useEditorStore()
const siteStore = useSiteStore()

// Enable keyboard shortcuts
const { cleanup: cleanupUndoRedo } = useUndoRedo()

// Enable auto-save
const { cleanup: cleanupAutoSave } = useAutoSave()

// Snackbar
const showSnackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

provide('showNotification', (text: string, color = 'success') => {
  snackbarText.value = text
  snackbarColor.value = color
  showSnackbar.value = true
})

onMounted(async () => {
  const siteId = route.params.siteId as string
  const pageId = route.params.pageId as string

  if (siteId) {
    await siteStore.loadSite(siteId)

    if (pageId) {
      siteStore.setCurrentPage(pageId)
      await editorStore.loadBlocks(siteId, pageId)
    } else if (siteStore.currentSite?.pages?.length) {
      // Default to first page
      const firstPage = siteStore.currentSite.pages[0]
      if (firstPage) {
        siteStore.setCurrentPage(firstPage.id)
        await editorStore.loadBlocks(siteId, firstPage.id)
      }
    }
  }

  // Load block templates
  await editorStore.loadTemplates()
})

onUnmounted(() => {
  cleanupUndoRedo()
  cleanupAutoSave()
})
</script>

<style scoped>
.editor-main {
  background-color: #f0f0f0;
  min-height: 100vh;
}
</style>
