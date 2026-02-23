<template>
  <!-- Top toolbar: save, preview, publish, undo/redo, device switching -->
  <v-app-bar density="compact" color="white" elevation="1" class="editor-toolbar">
    <!-- Left: back + page title -->
    <v-btn icon variant="text" @click="goBack">
      <v-icon>mdi-arrow-left</v-icon>
    </v-btn>

    <v-btn variant="text" size="small" @click="uiStore.togglePageList()">
      <v-icon left size="18">mdi-file-document-outline</v-icon>
      {{ siteStore.currentPage?.title || 'Page' }}
      <v-icon right size="18">mdi-chevron-down</v-icon>
    </v-btn>

    <v-divider vertical class="mx-2" />

    <!-- Undo/Redo -->
    <v-btn icon variant="text" size="small" :disabled="!editorStore.canUndo" @click="editorStore.undo()">
      <v-icon>mdi-undo</v-icon>
      <v-tooltip activator="parent" location="bottom">Undo (Ctrl+Z)</v-tooltip>
    </v-btn>
    <v-btn icon variant="text" size="small" :disabled="!editorStore.canRedo" @click="editorStore.redo()">
      <v-icon>mdi-redo</v-icon>
      <v-tooltip activator="parent" location="bottom">Redo (Ctrl+Shift+Z)</v-tooltip>
    </v-btn>

    <v-spacer />

    <!-- Device preview -->
    <DevicePreview />

    <v-spacer />

    <!-- Right: actions -->
    <v-btn variant="text" size="small" @click="uiStore.togglePageSettings()">
      <v-icon left size="18">mdi-magnify</v-icon>
      SEO
    </v-btn>

    <v-btn variant="text" size="small" @click="uiStore.toggleSiteSettings()">
      <v-icon left size="18">mdi-cog</v-icon>
      Site Settings
    </v-btn>

    <v-btn variant="text" size="small" :href="previewUrl" target="_blank">
      <v-icon left size="18">mdi-eye</v-icon>
      Preview
    </v-btn>

    <v-btn
      color="primary"
      variant="flat"
      size="small"
      :loading="editorStore.isSaving"
      @click="handleSave"
    >
      <v-icon left size="18">mdi-content-save</v-icon>
      Save
    </v-btn>

    <v-btn
      color="success"
      variant="flat"
      size="small"
      class="ml-2"
      @click="handlePublish"
    >
      <v-icon left size="18">mdi-rocket-launch</v-icon>
      Publish
    </v-btn>
  </v-app-bar>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useEditorStore } from '@/stores/editorStore'
import { useSiteStore } from '@/stores/siteStore'
import { useUiStore } from '@/stores/uiStore'
import DevicePreview from './DevicePreview.vue'

const router = useRouter()
const editorStore = useEditorStore()
const siteStore = useSiteStore()
const uiStore = useUiStore()

const previewUrl = computed(() => {
  if (!siteStore.currentSite || !siteStore.currentPage) return '#'
  return `/preview/${siteStore.currentSite.id}/${siteStore.currentPage.id}`
})

function goBack() {
  router.push('/')
}

async function handleSave() {
  await editorStore.save()
}

async function handlePublish() {
  await siteStore.publish()
}
</script>

<style scoped>
.editor-toolbar {
  border-bottom: 1px solid #e0e0e0;
}
</style>
