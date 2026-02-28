<template>
  <v-navigation-drawer
    v-model="show"
    location="right"
    width="360"
    temporary
    class="content-panel"
  >
    <div class="d-flex align-center pa-3">
      <span class="text-subtitle-1 font-weight-medium">Edit Content</span>
      <v-spacer />
      <v-btn icon variant="text" size="small" @click="close">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </div>

    <v-divider />

    <div v-if="!activeBlock" class="pa-6 text-center text-grey">
      <v-icon size="48" class="mb-2">mdi-pencil-off</v-icon>
      <p>Select a block to edit content</p>
    </div>

    <div v-else class="pa-4">
      <!-- Dynamic content fields based on block type -->
      <div class="mb-2 text-caption text-grey-darken-1">
        Editing: {{ activeBlock.type }} block
      </div>

      <!-- CRM Form block: special picker UI -->
      <template v-if="activeBlock.type === 'CrmFormBlock'">
        <v-card variant="outlined" class="mb-4 pa-3">
          <div class="text-subtitle-2 mb-3 d-flex align-center">
            <v-icon size="18" class="mr-2" color="primary">mdi-form-select</v-icon>
            CRM Form
          </div>
          <div v-if="activeBlock.content.formName" class="d-flex align-center mb-3">
            <v-chip color="primary" variant="tonal" size="small" prepend-icon="mdi-check-circle">
              {{ activeBlock.content.formName }}
            </v-chip>
            <v-btn icon variant="text" size="x-small" class="ml-1" @click="clearCrmForm">
              <v-icon size="14">mdi-close</v-icon>
            </v-btn>
          </div>
          <div v-else class="text-caption text-grey mb-3">No form selected</div>
          <v-btn
            color="primary"
            variant="tonal"
            size="small"
            block
            prepend-icon="mdi-plus"
            @click="showCrmFormPicker = true"
          >
            {{ activeBlock.content.formName ? 'Change Form' : 'Select CRM Form' }}
          </v-btn>
        </v-card>

        <!-- title / subtitle for CRM block -->
        <v-text-field
          :model-value="activeBlock.content.title"
          @update:model-value="updateContent('title', $event)"
          label="Title (optional)"
          density="compact"
          variant="outlined"
          hide-details
          class="mb-3"
        />
        <!-- font controls for CrmFormBlock title -->
        <div class="d-flex gap-1 mb-1">
          <v-text-field
            :model-value="activeBlock.content['titleFontSize'] || ''"
            @update:model-value="updateContent('titleFontSize', $event ? Number($event) : undefined)"
            placeholder="Size (px)"
            density="compact"
            variant="outlined"
            hide-details
            type="number"
            style="max-width: 84px; flex-shrink: 0"
          />
          <v-select
            :model-value="activeBlock.content['titleFontWeight'] || ''"
            @update:model-value="updateContent('titleFontWeight', $event || '')"
            :items="fontWeightOptions"
            density="compact"
            variant="outlined"
            hide-details
            clearable
            placeholder="Weight"
            class="flex-grow-1"
          />
        </div>
        <v-text-field
          :model-value="activeBlock.content.subtitle"
          @update:model-value="updateContent('subtitle', $event)"
          label="Subtitle (optional)"
          density="compact"
          variant="outlined"
          hide-details
          class="mb-1"
        />
        <!-- font controls for CrmFormBlock subtitle -->
        <div class="d-flex gap-1 mb-3">
          <v-text-field
            :model-value="activeBlock.content['subtitleFontSize'] || ''"
            @update:model-value="updateContent('subtitleFontSize', $event ? Number($event) : undefined)"
            placeholder="Size (px)"
            density="compact"
            variant="outlined"
            hide-details
            type="number"
            style="max-width: 84px; flex-shrink: 0"
          />
          <v-select
            :model-value="activeBlock.content['subtitleFontWeight'] || ''"
            @update:model-value="updateContent('subtitleFontWeight', $event || '')"
            :items="fontWeightOptions"
            density="compact"
            variant="outlined"
            hide-details
            clearable
            placeholder="Weight"
            class="flex-grow-1"
          />
        </div>

        <CrmFormPickerDialog
          v-model="showCrmFormPicker"
          @select="onCrmFormSelected"
        />
      </template>

      <!-- Generic content fields: iterate over content keys (skip CrmFormBlock special fields) -->
      <template v-if="activeBlock.type !== 'CrmFormBlock'">
        <template v-for="(value, key) in activeBlock.content" :key="key">

          <!-- Font size/weight controls — shown above every plain text field -->
          <template v-if="isSimpleField(key, value) && typeof value === 'string' && !isUrlField(key as string) && !isColorField(key as string)">
            <div class="d-flex gap-1 mb-1 align-center">
              <v-text-field
                :model-value="activeBlock.content[(key as string) + 'FontSize'] || ''"
                @update:model-value="updateContent((key as string) + 'FontSize', $event ? Number($event) : undefined)"
                placeholder="Size (px)"
                density="compact"
                variant="outlined"
                hide-details
                type="number"
                min="8"
                max="200"
                style="max-width: 84px; flex-shrink: 0"
              />
              <v-select
                :model-value="activeBlock.content[(key as string) + 'FontWeight'] || ''"
                @update:model-value="updateContent((key as string) + 'FontWeight', $event || '')"
                :items="fontWeightOptions"
                density="compact"
                variant="outlined"
                hide-details
                clearable
                placeholder="Weight"
                class="flex-grow-1"
              />
            </div>
          </template>

          <!-- Simple value fields -->
        <template v-if="isSimpleField(key, value)">
          <!-- URL fields -->
          <ImageUploader
            v-if="isImageField(key as string)"
            :model-value="value as string"
            @update:model-value="updateContent(key as string, $event)"
            :label="formatLabel(key as string)"
            class="mb-3"
          />
          <v-text-field
            v-else-if="isUrlField(key as string)"
            :model-value="value as string"
            @update:model-value="updateContent(key as string, $event)"
            :label="formatLabel(key as string)"
            density="compact"
            variant="outlined"
            hide-details
            class="mb-3"
            prepend-inner-icon="mdi-link"
          />

          <!-- Color fields -->
          <v-text-field
            v-else-if="isColorField(key as string)"
            :model-value="value as string"
            @update:model-value="updateContent(key as string, $event)"
            :label="formatLabel(key as string)"
            density="compact"
            variant="outlined"
            hide-details
            class="mb-3"
            prepend-inner-icon="mdi-palette"
          >
            <template #append-inner>
              <div
                class="color-swatch"
                :style="{ background: (value as string) || '#ffffff' }"
              />
            </template>
          </v-text-field>

          <!-- Rich text editor for long text fields -->
          <div v-else-if="isLongText(key as string, value as string)" class="mb-3">
            <div class="text-caption text-grey-darken-1 mb-1">{{ formatLabel(key as string) }}</div>
            <RichTextEditor
              :model-value="(value as string) || ''"
              @update:model-value="updateContent(key as string, $event)"
              :placeholder="formatLabel(key as string)"
            />
          </div>

          <!-- Number fields -->
          <v-text-field
            v-else-if="typeof value === 'number'"
            :model-value="value"
            @update:model-value="updateContent(key as string, Number($event))"
            :label="formatLabel(key as string)"
            density="compact"
            variant="outlined"
            hide-details
            class="mb-3"
            type="number"
          />

          <!-- Boolean fields -->
          <v-switch
            v-else-if="typeof value === 'boolean'"
            :model-value="value"
            @update:model-value="updateContent(key as string, $event)"
            :label="formatLabel(key as string)"
            color="primary"
            density="compact"
            hide-details
            class="mb-3"
          />

          <!-- Default: text field -->
          <v-text-field
            v-else
            :model-value="value as string"
            @update:model-value="updateContent(key as string, $event)"
            :label="formatLabel(key as string)"
            density="compact"
            variant="outlined"
            hide-details
            class="mb-3"
          />
        </template>

        <!-- Array fields (items, links, etc.) -->
        <template v-else-if="Array.isArray(value)">
          <div class="text-subtitle-2 mb-2">{{ formatLabel(key as string) }}</div>
          <v-card
            v-for="(item, idx) in (value as any[])"
            :key="idx"
            variant="outlined"
            class="pa-3 mb-2"
          >
            <div class="d-flex align-center mb-2">
              <span class="text-caption text-grey">Item {{ idx + 1 }}</span>
              <v-spacer />
              <v-btn icon variant="text" size="x-small" @click="removeArrayItem(key as string, idx)">
                <v-icon size="16">mdi-delete-outline</v-icon>
              </v-btn>
            </div>
            <template v-if="typeof item === 'object' && item !== null">
              <template v-for="(subVal, subKey) in item" :key="subKey">
                <v-text-field
                  v-if="typeof subVal === 'string' || typeof subVal === 'number'"
                  :model-value="subVal"
                  @update:model-value="updateArrayItemField(key as string, idx, subKey as string, $event)"
                  :label="formatLabel(subKey as string)"
                  density="compact"
                  variant="outlined"
                  hide-details
                  class="mb-2"
                />
              </template>
            </template>
            <v-text-field
              v-else
              :model-value="item"
              @update:model-value="updateArrayItem(key as string, idx, $event)"
              :label="`Value`"
              density="compact"
              variant="outlined"
              hide-details
            />
          </v-card>
          <v-btn
            variant="tonal"
            size="small"
            color="primary"
            block
            class="mb-4"
            @click="addArrayItem(key as string)"
          >
            <v-icon left size="16">mdi-plus</v-icon>
            Add Item
          </v-btn>
        </template>
        </template>
      </template>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useEditorStore } from '@/stores/editorStore'
import { useUiStore } from '@/stores/uiStore'
import { deepClone } from '@/utils/helpers'
import CrmFormPickerDialog from '@/components/common/CrmFormPickerDialog.vue'
import ImageUploader from '@/components/common/ImageUploader.vue'
import RichTextEditor from '@/components/common/RichTextEditor.vue'

const showCrmFormPicker = ref(false)

function onCrmFormSelected(data: { formId: string; formName: string; formSlug: string; embedCode: string }) {
  if (!activeBlock.value) return
  editorStore.updateBlockContent(activeBlock.value.id, {
    formId: data.formId,
    formName: data.formName,
    formSlug: data.formSlug,
    embedCode: data.embedCode,
  })
}

function clearCrmForm() {
  if (!activeBlock.value) return
  editorStore.updateBlockContent(activeBlock.value.id, {
    formId: '',
    formName: '',
    formSlug: '',
    embedCode: '',
  })
}

const editorStore = useEditorStore()
const uiStore = useUiStore()

// Font weight options for the typography controls
const fontWeightOptions = ['100', '200', '300', '400', '500', '600', '700', '800', '900']

const show = computed({
  get: () => uiStore.showContentPanel,
  set: (val: boolean) => {
    if (!val) uiStore.closeContentPanel()
  },
})

const activeBlock = computed(() => {
  if (!editorStore.activeBlockId) return null
  return editorStore.blocks.find((b) => b.id === editorStore.activeBlockId) || null
})

function isSimpleField(key: string | number, value: unknown): boolean {
  // Skip typography meta-keys generated by the font controls
  if (isTypographyKey(String(key))) return false
  return typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean'
}

function isTypographyKey(key: string): boolean {
  return key.endsWith('FontSize') || key.endsWith('FontWeight')
}

function isUrlField(key: string): boolean {
  const urlKeys = ['url', 'href', 'link', 'src', 'image', 'imageUrl', 'backgroundImage', 'videoUrl']
  return urlKeys.some((k) => key.toLowerCase().includes(k.toLowerCase()))
}

// Image-specific fields that should show the ImageUploader (with upload button)
function isImageField(key: string): boolean {
  const imageKeys = ['image', 'imageUrl', 'backgroundImage', 'photo', 'avatar', 'thumbnail', 'src']
  return imageKeys.some((k) => key.toLowerCase().includes(k.toLowerCase()))
}

function isColorField(key: string): boolean {
  return key.toLowerCase().includes('color')
}

function isLongText(key: string, value: string): boolean {
  const k = key.toLowerCase()
  // Always rich text for these field name patterns (exact or suffix)
  const richPatterns = ['subtitle', 'description', 'body', 'paragraph', 'content']
  if (richPatterns.some((p) => k === p || k.endsWith(p))) return true
  // 'text' field or fields ending with 'text' — but not button/cta/submit labels
  if (k === 'text' || k.endsWith('text')) {
    if (k.includes('button') || k.includes('submit') || k.includes('cta') || k.includes('placeholder')) return false
    return true
  }
  return false
}

function formatLabel(key: string): string {
  return key
    .replace(/([A-Z])/g, ' $1')
    .replace(/[_-]/g, ' ')
    .replace(/^./, (s) => s.toUpperCase())
    .trim()
}

function updateContent(key: string, value: any) {
  if (!activeBlock.value) return
  editorStore.updateBlockContent(activeBlock.value.id, { [key]: value })
}

function updateArrayItem(key: string, index: number, value: any) {
  if (!activeBlock.value) return
  const arr = deepClone(activeBlock.value.content[key] as any[])
  arr[index] = value
  editorStore.updateBlockContent(activeBlock.value.id, { [key]: arr })
}

function updateArrayItemField(key: string, index: number, field: string, value: any) {
  if (!activeBlock.value) return
  const arr = deepClone(activeBlock.value.content[key] as any[])
  arr[index] = { ...arr[index], [field]: value }
  editorStore.updateBlockContent(activeBlock.value.id, { [key]: arr })
}

function removeArrayItem(key: string, index: number) {
  if (!activeBlock.value) return
  const arr = deepClone(activeBlock.value.content[key] as any[])
  arr.splice(index, 1)
  editorStore.updateBlockContent(activeBlock.value.id, { [key]: arr })
}

function addArrayItem(key: string) {
  if (!activeBlock.value) return
  const arr = deepClone(activeBlock.value.content[key] as any[])
  // Create a default item based on existing items
  if (arr.length > 0 && typeof arr[0] === 'object') {
    const template: Record<string, any> = {}
    for (const k of Object.keys(arr[0])) {
      template[k] = typeof arr[0][k] === 'number' ? 0 : ''
    }
    arr.push(template)
  } else {
    arr.push('')
  }
  editorStore.updateBlockContent(activeBlock.value.id, { [key]: arr })
}

function close() {
  uiStore.closeContentPanel()
}
</script>

<style scoped>
.content-panel {
  z-index: 1010;
}

.color-swatch {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}
</style>
