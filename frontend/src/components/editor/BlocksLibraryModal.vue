<template>
  <v-navigation-drawer
    v-model="show"
    location="right"
    :width="300"
    class="blocks-library-drawer"
    style="z-index: 1006"
  >
    <!-- Header -->
    <div class="blocks-library-header pa-3 d-flex align-center">
      <span class="text-subtitle-1 font-weight-medium">Blocks</span>
      <v-spacer />
      <v-btn icon variant="text" size="small" @click="close">
        <v-icon size="20">mdi-close</v-icon>
      </v-btn>
    </div>

    <v-divider />

    <!-- Search -->
    <div class="px-3 py-2">
      <v-text-field
        v-model="search"
        density="compact"
        variant="outlined"
        placeholder="Search blocks..."
        prepend-inner-icon="mdi-magnify"
        hide-details
        clearable
      />
    </div>

    <v-divider />

    <!-- Categories with expandable block lists -->
    <div class="blocks-library-list">
      <!-- Search results (flat list, no categories) -->
      <template v-if="search">
        <div v-if="searchResults.length === 0" class="text-center py-8 text-grey">
          <v-icon size="40" class="mb-2">mdi-package-variant</v-icon>
          <p class="text-body-2">No blocks found</p>
        </div>
        <div
          v-for="template in searchResults"
          :key="template.type"
          class="block-template-item d-flex align-center px-4 py-2"
          @click="selectTemplate(template)"
        >
          <v-icon size="22" color="primary" class="mr-3 flex-shrink-0">
            {{ getBlockIcon(template.category) }}
          </v-icon>
          <div class="flex-grow-1 overflow-hidden">
            <div class="text-body-2 font-weight-medium text-truncate">{{ template.name }}</div>
            <div class="text-caption text-medium-emphasis">{{ categoryLabel(template.category) }}</div>
          </div>
        </div>
      </template>

      <!-- Expandable category groups -->
      <template v-else>
        <div v-for="cat in categoriesWithTemplates" :key="cat.key" class="category-group">
          <!-- Category header (clickable to expand/collapse) -->
          <div
            class="category-header d-flex align-center px-3 py-2"
            @click="toggleCategory(cat.key)"
          >
            <v-icon size="20" class="mr-2" color="grey-darken-1">
              {{ getBlockIcon(cat.key) }}
            </v-icon>
            <span class="text-body-2 font-weight-medium flex-grow-1">{{ cat.label }}</span>
            <span class="text-caption text-medium-emphasis mr-1">{{ cat.templates.length }}</span>
            <v-icon size="18" color="grey">
              {{ expandedCategories.has(cat.key) ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
            </v-icon>
          </div>

          <!-- Expanded block list -->
          <v-expand-transition>
            <div v-show="expandedCategories.has(cat.key)">
              <div
                v-for="template in cat.templates"
                :key="template.type"
                class="block-template-item d-flex align-center pl-10 pr-3 py-2"
                @click="selectTemplate(template)"
              >
                <div class="flex-grow-1 overflow-hidden">
                  <div class="text-body-2 text-truncate">{{ template.name }}</div>
                </div>
                <v-icon size="16" color="grey-lighten-1" class="flex-shrink-0">mdi-plus</v-icon>
              </div>
            </div>
          </v-expand-transition>
        </div>
      </template>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive } from 'vue'
import { useEditorStore } from '@/stores/editorStore'
import { useUiStore } from '@/stores/uiStore'
import type { IBlockTemplate } from '@/types/block'
import { BlockCategory } from '@/types/block'
import { categoryLabel } from '@/utils/helpers'

const editorStore = useEditorStore()
const uiStore = useUiStore()

const search = ref('')
const expandedCategories = reactive(new Set<string>())

const show = computed({
  get: () => uiStore.showBlocksLibrary,
  set: (val: boolean) => {
    if (!val) uiStore.closeBlocksLibrary()
  },
})

// Group templates by category
const categoriesWithTemplates = computed(() => {
  const cats = Object.values(BlockCategory)
  return cats
    .map((cat) => ({
      key: cat,
      label: categoryLabel(cat),
      templates: editorStore.templates.filter((t) => t.category === cat),
    }))
    .filter((cat) => cat.templates.length > 0)
})

// Flat search results
const searchResults = computed(() => {
  if (!search.value) return []
  const q = search.value.toLowerCase()
  return editorStore.templates.filter(
    (t) =>
      t.name.toLowerCase().includes(q) ||
      t.type.toLowerCase().includes(q) ||
      t.category.toLowerCase().includes(q)
  )
})

function toggleCategory(key: string) {
  if (expandedCategories.has(key)) {
    expandedCategories.delete(key)
  } else {
    expandedCategories.add(key)
  }
}

function getBlockIcon(category: string): string {
  const icons: Record<string, string> = {
    cover: 'mdi-image-area',
    about: 'mdi-account-box-outline',
    text: 'mdi-text',
    heading: 'mdi-format-header-1',
    image: 'mdi-image-outline',
    gallery: 'mdi-view-grid-outline',
    button: 'mdi-gesture-tap-button',
    form: 'mdi-form-textbox',
    menu: 'mdi-menu',
    footer: 'mdi-page-layout-footer',
    video: 'mdi-video-outline',
    divider: 'mdi-minus',
    columns: 'mdi-view-column-outline',
    zeroblock: 'mdi-vector-arrange-below',
  }
  return icons[category] || 'mdi-puzzle-outline'
}

function selectTemplate(template: IBlockTemplate) {
  editorStore.addBlock(template.type, template.category, uiStore.insertAfterBlockId || undefined)
  close()
}

function close() {
  uiStore.closeBlocksLibrary()
  search.value = ''
}

// Load templates on first open
watch(show, (val) => {
  if (val && editorStore.templates.length === 0) {
    editorStore.loadTemplates()
  }
})
</script>

<style scoped>
.blocks-library-drawer {
  border-left: 1px solid rgba(0, 0, 0, 0.12);
}

.blocks-library-header {
  min-height: 48px;
}

.blocks-library-list {
  overflow-y: auto;
  height: calc(100vh - 160px);
}

.category-group {
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.category-header {
  cursor: pointer;
  transition: background-color 0.15s ease;
  min-height: 40px;
}

.category-header:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.block-template-item {
  cursor: pointer;
  transition: background-color 0.15s ease;
  min-height: 36px;
}

.block-template-item:hover {
  background-color: rgba(25, 118, 210, 0.08);
}

.block-template-item:active {
  background-color: rgba(25, 118, 210, 0.15);
}
</style>
