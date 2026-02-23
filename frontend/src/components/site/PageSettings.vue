<template>
  <v-dialog v-model="show" max-width="500">
    <v-card>
      <v-card-title class="d-flex align-center pa-4">
        <span class="text-h6">Page Settings</span>
        <v-spacer />
        <v-btn icon variant="text" @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-4">
        <v-text-field
          v-model="form.title"
          label="Page Title"
          variant="outlined"
          density="compact"
          class="mb-3"
        />

        <v-text-field
          v-model="form.slug"
          label="URL Slug"
          variant="outlined"
          density="compact"
          prefix="/"
          class="mb-3"
        />

        <v-switch
          v-model="form.isHomePage"
          label="Home Page"
          color="primary"
          density="compact"
          hide-details
          class="mb-4"
        />

        <div class="text-subtitle-2 mb-2">SEO Settings</div>

        <v-text-field
          v-model="form.seo.title"
          label="SEO Title"
          variant="outlined"
          density="compact"
          class="mb-3"
          counter="60"
        />

        <v-textarea
          v-model="form.seo.description"
          label="Meta Description"
          variant="outlined"
          density="compact"
          rows="3"
          class="mb-3"
          counter="160"
        />

        <v-text-field
          v-model="form.seo.ogImage"
          label="OG Image URL"
          variant="outlined"
          density="compact"
          prepend-inner-icon="mdi-image"
          class="mb-3"
        />

        <v-text-field
          v-model="form.seo.canonicalUrl"
          label="Canonical URL"
          variant="outlined"
          density="compact"
          prepend-inner-icon="mdi-link"
          class="mb-3"
        />

        <v-switch
          v-model="form.seo.noIndex"
          label="No Index (hide from search engines)"
          color="warning"
          density="compact"
          hide-details
        />
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" @click="close">Cancel</v-btn>
        <v-btn color="primary" variant="flat" @click="save">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { useSiteStore } from '@/stores/siteStore'
import { useUiStore } from '@/stores/uiStore'

const siteStore = useSiteStore()
const uiStore = useUiStore()

const form = reactive({
  title: '',
  slug: '',
  isHomePage: false,
  seo: {
    title: '',
    description: '',
    ogImage: '',
    canonicalUrl: '',
    noIndex: false,
  },
})

const show = computed({
  get: () => uiStore.showPageSettings,
  set: (val: boolean) => {
    if (!val) uiStore.closePageSettings()
  },
})

watch(show, (val) => {
  if (val && siteStore.currentPage) {
    const page = siteStore.currentPage
    form.title = page.title
    form.slug = page.slug
    form.isHomePage = page.isHomePage || false
    form.seo.title = page.seo?.title || ''
    form.seo.description = page.seo?.description || ''
    form.seo.ogImage = page.seo?.ogImage || ''
    form.seo.canonicalUrl = page.seo?.canonicalUrl || ''
    form.seo.noIndex = page.seo?.noIndex || false
  }
})

async function save() {
  if (!siteStore.currentSite || !siteStore.currentPage) return
  await siteStore.savePage(siteStore.currentSite.id, {
    ...siteStore.currentPage,
    title: form.title,
    slug: form.slug,
    isMain: form.isHomePage,
    isHomePage: form.isHomePage,
    seo: { ...form.seo },
  } as any)
  close()
}

function close() {
  uiStore.closePageSettings()
}
</script>
