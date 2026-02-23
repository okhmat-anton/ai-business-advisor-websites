<template>
  <v-navigation-drawer
    v-model="show"
    location="right"
    width="320"
    temporary
    class="settings-panel"
  >
    <div class="d-flex align-center pa-3">
      <span class="text-subtitle-1 font-weight-medium">Block Settings</span>
      <v-spacer />
      <v-btn icon variant="text" size="small" @click="close">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </div>

    <v-divider />

    <div v-if="!activeBlock" class="pa-6 text-center text-grey">
      <v-icon size="48" class="mb-2">mdi-cog-off-outline</v-icon>
      <p>Select a block to edit settings</p>
    </div>

    <div v-else class="pa-4">
      <!-- Block type info -->
      <div class="mb-4 text-caption text-grey-darken-1">
        {{ activeBlock.type }} | {{ activeBlock.category }}
      </div>

      <!-- Padding -->
      <div class="setting-group">
        <div class="text-subtitle-2 mb-2">Padding</div>

        <v-row dense>
          <v-col cols="6">
            <v-text-field
              :model-value="settings.paddingTop"
              @update:model-value="updateSetting('paddingTop', $event)"
              label="Top"
              type="number"
              suffix="px"
              density="compact"
              variant="outlined"
              hide-details
            />
          </v-col>
          <v-col cols="6">
            <v-text-field
              :model-value="settings.paddingBottom"
              @update:model-value="updateSetting('paddingBottom', $event)"
              label="Bottom"
              type="number"
              suffix="px"
              density="compact"
              variant="outlined"
              hide-details
            />
          </v-col>
        </v-row>
      </div>

      <!-- Background color -->
      <div class="setting-group">
        <div class="text-subtitle-2 mb-2">Background Color</div>
        <v-text-field
          :model-value="settings.backgroundColor"
          @update:model-value="updateSetting('backgroundColor', $event)"
          label="Color"
          density="compact"
          variant="outlined"
          hide-details
          prepend-inner-icon="mdi-palette"
        >
          <template #append-inner>
            <div
              class="color-swatch"
              :style="{ background: settings.backgroundColor || '#ffffff' }"
            />
          </template>
        </v-text-field>

        <!-- Quick color presets -->
        <div class="d-flex flex-wrap gap-1 mt-2">
          <div
            v-for="color in colorPresets"
            :key="color"
            class="color-preset"
            :class="{ active: settings.backgroundColor === color }"
            :style="{ background: color }"
            @click="updateSetting('backgroundColor', color)"
          />
        </div>
      </div>

      <!-- Background image -->
      <div class="setting-group">
        <div class="text-subtitle-2 mb-2">Background Image</div>
        <v-text-field
          :model-value="settings.backgroundImage"
          @update:model-value="updateSetting('backgroundImage', $event)"
          label="Image URL"
          density="compact"
          variant="outlined"
          hide-details
          prepend-inner-icon="mdi-image"
        />
      </div>

      <!-- Full width -->
      <div class="setting-group">
        <v-switch
          :model-value="settings.fullWidth"
          @update:model-value="updateSetting('fullWidth', $event)"
          label="Full Width"
          color="primary"
          density="compact"
          hide-details
        />
      </div>

      <!-- Visibility per device -->
      <div class="setting-group">
        <div class="text-subtitle-2 mb-2">Visibility</div>
        <v-switch
          :model-value="settings.hideOnMobile"
          @update:model-value="updateSetting('hideOnMobile', $event)"
          label="Hide on Mobile"
          color="primary"
          density="compact"
          hide-details
        />
        <v-switch
          :model-value="settings.hideOnDesktop"
          @update:model-value="updateSetting('hideOnDesktop', $event)"
          label="Hide on Desktop"
          color="primary"
          density="compact"
          hide-details
        />
      </div>

      <!-- CSS class -->
      <div class="setting-group">
        <div class="text-subtitle-2 mb-2">Advanced</div>
        <v-text-field
          :model-value="settings.cssClass"
          @update:model-value="updateSetting('cssClass', $event)"
          label="CSS Class"
          density="compact"
          variant="outlined"
          hide-details
          prepend-inner-icon="mdi-code-braces"
        />
        <v-text-field
          :model-value="settings.anchor"
          @update:model-value="updateSetting('anchor', $event)"
          label="Anchor ID"
          density="compact"
          variant="outlined"
          hide-details
          prepend-inner-icon="mdi-pound"
          class="mt-2"
        />
      </div>

      <!-- Animation -->
      <div class="setting-group">
        <div class="text-subtitle-2 mb-2">Animation</div>
        <v-select
          :model-value="settings.animation"
          @update:model-value="updateSetting('animation', $event)"
          :items="animationOptions"
          label="Animation Type"
          density="compact"
          variant="outlined"
          hide-details
        />
      </div>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { useEditorStore } from '@/stores/editorStore'
import { useUiStore } from '@/stores/uiStore'
import { DEFAULT_BLOCK_SETTINGS } from '@/types/block'

const editorStore = useEditorStore()
const uiStore = useUiStore()

const show = computed({
  get: () => uiStore.showSettingsPanel,
  set: (val: boolean) => {
    if (!val) uiStore.closeSettingsPanel()
  },
})

const activeBlock = computed(() => {
  if (!editorStore.activeBlockId) return null
  return editorStore.blocks.find((b) => b.id === editorStore.activeBlockId) || null
})

const settings = computed(() => {
  return activeBlock.value?.settings || { ...DEFAULT_BLOCK_SETTINGS }
})

const colorPresets = [
  '#ffffff',
  '#f5f5f5',
  '#e0e0e0',
  '#212121',
  '#1a1a2e',
  '#0f3460',
  '#e94560',
  '#16213e',
  '#533483',
  '#2b2d42',
  '#ef233c',
  '#f72585',
]

const animationOptions = [
  { title: 'None', value: 'none' },
  { title: 'Fade In', value: 'fadeIn' },
  { title: 'Slide Up', value: 'slideUp' },
  { title: 'Slide Left', value: 'slideLeft' },
  { title: 'Slide Right', value: 'slideRight' },
  { title: 'Zoom In', value: 'zoomIn' },
]

function updateSetting(key: string, value: any) {
  if (!activeBlock.value) return
  editorStore.updateBlockSettings(activeBlock.value.id, { [key]: value })
}

function close() {
  uiStore.closeSettingsPanel()
}
</script>

<style scoped>
.settings-panel {
  z-index: 1010;
}

.setting-group {
  margin-bottom: 20px;
}

.color-swatch {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.color-preset {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.15s;
}

.color-preset:hover {
  transform: scale(1.1);
}

.color-preset.active {
  border-color: rgb(var(--v-theme-primary));
  box-shadow: 0 0 0 1px rgb(var(--v-theme-primary));
}

.gap-1 {
  gap: 6px;
}
</style>
