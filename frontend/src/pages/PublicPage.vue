<template>
  <div class="public-page">
    <div v-if="loading" class="loading">
      <v-progress-circular indeterminate color="primary" size="48" />
    </div>

    <div v-else-if="error" class="error-state">
      <v-icon size="64" color="grey">mdi-alert-circle-outline</v-icon>
      <h2 class="text-h5 mt-4">Page Not Found</h2>
      <p class="text-body-2 text-grey mt-2">{{ error }}</p>
      <v-btn color="primary" variant="flat" class="mt-4" to="/">Go Home</v-btn>
    </div>

    <div v-else class="public-content">
      <template v-for="block in sortedBlocks" :key="block.id">
        <BlockRenderer :block="block" />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useEditorStore } from '@/stores/editorStore'
import { useSiteStore } from '@/stores/siteStore'
import BlockRenderer from '@/components/editor/BlockRenderer.vue'

const route = useRoute()
const editorStore = useEditorStore()
const siteStore = useSiteStore()

const loading = ref(true)
const error = ref('')

const sortedBlocks = computed(() =>
  [...editorStore.blocks].sort((a, b) => a.order - b.order)
)

onMounted(async () => {
  try {
    const slug = route.params.slug as string
    // In real app, this would fetch by domain/slug
    // For mock, load the first published site
    await siteStore.loadSites()

    const site = siteStore.sites[0]
    if (!site) {
      error.value = 'No published sites found'
      return
    }

    await siteStore.loadSite(site.id)

    const page = site.pages?.find((p) => p.slug === slug) || site.pages?.[0]
    if (!page) {
      error.value = 'Page not found'
      return
    }

    siteStore.setCurrentPage(page.id)
    await editorStore.loadBlocks(site.id, page.id)
  } catch (e) {
    error.value = 'Failed to load page'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.public-page {
  min-height: 100vh;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

.public-content {
  min-height: 100vh;
}
</style>
