<template>
  <v-navigation-drawer
    v-model="show"
    location="left"
    width="280"
    temporary
    class="page-list-panel"
  >
    <div class="d-flex align-center pa-3">
      <span class="text-subtitle-1 font-weight-medium">Pages</span>
      <v-spacer />
      <v-btn icon variant="text" size="small" @click="addPage">
        <v-icon>mdi-plus</v-icon>
        <v-tooltip activator="parent" location="bottom">Add Page</v-tooltip>
      </v-btn>
      <v-btn icon variant="text" size="small" @click="close">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </div>

    <v-divider />

    <v-list density="compact" nav>
      <v-list-item
        v-for="page in pages"
        :key="page.id"
        :active="page.id === siteStore.currentPage?.id"
        @click="selectPage(page.id)"
        rounded="lg"
      >
        <template #prepend>
          <v-icon size="18">mdi-file-document-outline</v-icon>
        </template>

        <v-list-item-title>{{ page.title }}</v-list-item-title>
        <v-list-item-subtitle class="text-caption">
          /{{ page.slug }}
          <v-chip
            v-if="page.isHomePage"
            size="x-small"
            color="primary"
            class="ml-1"
          >
            Home
          </v-chip>
        </v-list-item-subtitle>

        <template #append>
          <v-menu>
            <template #activator="{ props }">
              <v-btn icon variant="text" size="x-small" v-bind="props">
                <v-icon size="16">mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list density="compact">
              <v-list-item @click="editPageSettings(page.id)">
                <template #prepend>
                  <v-icon size="16">mdi-cog</v-icon>
                </template>
                <v-list-item-title>Settings</v-list-item-title>
              </v-list-item>
              <v-list-item @click="duplicatePage(page)">
                <template #prepend>
                  <v-icon size="16">mdi-content-copy</v-icon>
                </template>
                <v-list-item-title>Duplicate</v-list-item-title>
              </v-list-item>
              <v-divider />
              <v-list-item
                @click="deletePage(page.id)"
                :disabled="page.isHomePage"
              >
                <template #prepend>
                  <v-icon size="16" color="error">mdi-delete</v-icon>
                </template>
                <v-list-item-title class="text-error">Delete</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </template>
      </v-list-item>
    </v-list>

    <div v-if="pages.length === 0" class="pa-6 text-center text-grey">
      <v-icon size="48" class="mb-2">mdi-file-plus-outline</v-icon>
      <p>No pages yet</p>
      <v-btn variant="tonal" color="primary" size="small" @click="addPage">
        Create First Page
      </v-btn>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSiteStore } from '@/stores/siteStore'
import { useUiStore } from '@/stores/uiStore'
import { useEditorStore } from '@/stores/editorStore'
import type { IPage } from '@/types/site'

const siteStore = useSiteStore()
const uiStore = useUiStore()
const editorStore = useEditorStore()

const show = computed({
  get: () => uiStore.showPageList,
  set: (val: boolean) => {
    if (!val) uiStore.closePageList()
  },
})

const pages = computed(() => siteStore.currentSite?.pages || [])

async function selectPage(pageId: string) {
  siteStore.setCurrentPage(pageId)
  await editorStore.loadBlocks(siteStore.currentSite!.id, pageId)
  close()
}

async function addPage() {
  if (!siteStore.currentSite) return
  const title = `Page ${pages.value.length + 1}`
  await siteStore.addPage(siteStore.currentSite.id, title)
}

async function duplicatePage(page: IPage) {
  if (!siteStore.currentSite) return
  await siteStore.addPage(siteStore.currentSite.id, `${page.title} (copy)`)
}

async function deletePage(pageId: string) {
  if (!siteStore.currentSite) return
  await siteStore.removePage(siteStore.currentSite.id, pageId)
}

function editPageSettings(pageId: string) {
  siteStore.setCurrentPage(pageId)
  uiStore.openPageSettings()
}

function close() {
  uiStore.closePageList()
}
</script>

<style scoped>
.page-list-panel {
  z-index: 1010;
}
</style>
