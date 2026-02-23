<template>
  <div class="preview-page">
    <!-- Preview toolbar -->
    <div class="preview-toolbar">
      <v-btn icon variant="text" size="small" @click="goBack">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <span class="text-subtitle-2 mx-3">Preview: {{ siteStore.currentPage?.title }}</span>

      <v-spacer />

      <v-btn-toggle v-model="deviceMode" density="compact" variant="outlined" divided mandatory>
        <v-btn value="desktop" size="small"><v-icon size="18">mdi-monitor</v-icon></v-btn>
        <v-btn value="tablet" size="small"><v-icon size="18">mdi-tablet</v-icon></v-btn>
        <v-btn value="mobile" size="small"><v-icon size="18">mdi-cellphone</v-icon></v-btn>
      </v-btn-toggle>

      <v-spacer />

      <v-btn variant="text" size="small" @click="goBack">
        Back to Editor
      </v-btn>
    </div>

    <!-- Preview frame -->
    <div class="preview-frame" :style="frameStyle">
      <div class="preview-content">
        <template v-for="block in sortedBlocks" :key="block.id">
          <BlockRenderer :block="block" />
        </template>

        <div v-if="sortedBlocks.length === 0" class="empty-preview">
          <v-icon size="48" color="grey-lighten-1">mdi-eye-off</v-icon>
          <p class="text-body-2 text-grey mt-2">No blocks to preview</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEditorStore } from '@/stores/editorStore'
import { useSiteStore } from '@/stores/siteStore'
import { DEVICE_SIZES } from '@/types/editor'
import BlockRenderer from '@/components/editor/BlockRenderer.vue'

const route = useRoute()
const router = useRouter()
const editorStore = useEditorStore()
const siteStore = useSiteStore()

const deviceMode = ref('desktop')

const sortedBlocks = computed(() =>
  [...editorStore.blocks].sort((a, b) => a.order - b.order)
)

const frameStyle = computed(() => {
  const sizes = DEVICE_SIZES[deviceMode.value as keyof typeof DEVICE_SIZES]
  return {
    maxWidth: sizes ? `${sizes.width}px` : '100%',
    margin: '0 auto',
  }
})

function goBack() {
  const siteId = route.params.siteId as string
  const pageId = route.params.pageId as string
  router.push(`/editor/${siteId}/${pageId}`)
}

onMounted(async () => {
  const siteId = route.params.siteId as string
  const pageId = route.params.pageId as string

  if (siteId && !siteStore.currentSite) {
    await siteStore.loadSite(siteId)
  }
  if (pageId && editorStore.blocks.length === 0) {
    siteStore.setCurrentPage(pageId)
    await editorStore.loadBlocks(siteId, pageId)
  }
})
</script>

<style scoped>
.preview-page {
  min-height: 100vh;
  background: #e0e0e0;
}

.preview-toolbar {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.preview-frame {
  background: white;
  min-height: calc(100vh - 48px);
  transition: max-width 0.3s ease;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

.preview-content {
  min-height: 100%;
}

.empty-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
}
</style>
