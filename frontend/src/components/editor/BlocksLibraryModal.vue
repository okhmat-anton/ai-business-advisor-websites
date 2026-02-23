<template>
  <v-dialog v-model="show" max-width="900" scrollable>
    <v-card class="blocks-library">
      <v-card-title class="d-flex align-center pa-4">
        <span class="text-h6">Block Library</span>
        <v-spacer />
        <v-text-field
          v-model="search"
          density="compact"
          variant="outlined"
          placeholder="Search blocks..."
          prepend-inner-icon="mdi-magnify"
          hide-details
          clearable
          class="search-field"
        />
        <v-btn icon variant="text" class="ml-2" @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <!-- Category tabs -->
      <v-tabs v-model="activeTab" color="primary" density="compact" show-arrows>
        <v-tab value="all">All</v-tab>
        <v-tab v-for="cat in categories" :key="cat" :value="cat">
          {{ categoryLabel(cat) }}
        </v-tab>
      </v-tabs>

      <v-divider />

      <v-card-text class="pa-4" style="min-height: 400px; max-height: 60vh;">
        <div v-if="filteredTemplates.length === 0" class="text-center py-8 text-grey">
          <v-icon size="48" class="mb-2">mdi-package-variant</v-icon>
          <p>No blocks found</p>
        </div>

        <v-row v-else>
          <v-col
            v-for="template in filteredTemplates"
            :key="template.type"
            cols="6"
            sm="4"
            md="3"
          >
            <v-card
              variant="outlined"
              class="block-template-card pa-3 text-center"
              hover
              @click="selectTemplate(template)"
            >
              <v-icon size="32" color="primary" class="mb-2">
                {{ getBlockIcon(template.category) }}
              </v-icon>
              <div class="text-body-2 font-weight-medium">{{ template.name }}</div>
              <div class="text-caption text-grey">{{ template.category }}</div>

              <!-- Preview thumbnail -->
              <div class="template-preview mt-2">
                <div class="preview-placeholder" />
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useEditorStore } from '@/stores/editorStore'
import { useUiStore } from '@/stores/uiStore'
import type { IBlockTemplate } from '@/types/block'
import { BlockCategory } from '@/types/block'
import { categoryLabel } from '@/utils/helpers'

const editorStore = useEditorStore()
const uiStore = useUiStore()

const search = ref('')
const activeTab = ref('all')

const show = computed({
  get: () => uiStore.showBlocksLibrary,
  set: (val: boolean) => {
    if (!val) uiStore.closeBlocksLibrary()
  },
})

const categories = computed(() => Object.values(BlockCategory))

const filteredTemplates = computed(() => {
  let templates = editorStore.templates

  // Filter by category tab
  if (activeTab.value !== 'all') {
    templates = templates.filter((t) => t.category === activeTab.value)
  }

  // Filter by search
  if (search.value) {
    const q = search.value.toLowerCase()
    templates = templates.filter(
      (t) =>
        t.name.toLowerCase().includes(q) ||
        t.type.toLowerCase().includes(q) ||
        t.category.toLowerCase().includes(q)
    )
  }

  return templates
})

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
  activeTab.value = 'all'
}

// Load templates on first open
watch(show, (val) => {
  if (val && editorStore.templates.length === 0) {
    editorStore.loadTemplates()
  }
})
</script>

<style scoped>
.blocks-library {
  border-radius: 8px;
}

.search-field {
  max-width: 250px;
}

.block-template-card {
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 8px;
}

.block-template-card:hover {
  border-color: rgb(var(--v-theme-primary));
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.template-preview {
  border-radius: 4px;
  overflow: hidden;
}

.preview-placeholder {
  height: 60px;
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
  border-radius: 4px;
}
</style>
