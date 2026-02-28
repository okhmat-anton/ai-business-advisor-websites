<template>
  <!-- Wrapper around each block in edit mode with control buttons -->
  <div
    ref="wrapperRef"
    class="block-wrapper"
    :class="{ 'block-wrapper--active': isActive, 'block-wrapper--resizing': resizing }"
    :style="wrapperStyle"
    @click.stop="selectBlock"
  >
    <!-- Block controls overlay -->
    <div v-if="isActive" class="block-controls">
      <div class="block-controls-left">
        <v-btn icon size="small" variant="flat" color="primary" @click.stop="$emit('openContent')">
          <v-icon size="18">mdi-pencil</v-icon>
          <v-tooltip activator="parent" location="top">Content</v-tooltip>
        </v-btn>
        <v-btn icon size="small" variant="flat" color="primary" @click.stop="$emit('openSettings')">
          <v-icon size="18">mdi-cog</v-icon>
          <v-tooltip activator="parent" location="top">Settings</v-tooltip>
        </v-btn>
      </div>
      <div class="block-controls-right">
        <v-btn icon size="x-small" variant="text" @click.stop="$emit('moveUp')" :disabled="isFirst">
          <v-icon size="18">mdi-arrow-up</v-icon>
        </v-btn>
        <v-btn icon size="x-small" variant="text" @click.stop="$emit('moveDown')" :disabled="isLast">
          <v-icon size="18">mdi-arrow-down</v-icon>
        </v-btn>
        <v-btn icon size="x-small" variant="text" @click.stop="$emit('duplicate')">
          <v-icon size="18">mdi-content-copy</v-icon>
        </v-btn>
        <v-btn icon size="x-small" variant="text" color="error" @click.stop="$emit('remove')">
          <v-icon size="18">mdi-delete</v-icon>
        </v-btn>
      </div>
    </div>

    <!-- The actual block content -->
    <BlockRenderer :block="block" />

    <!-- Height resize handle — shows on hover/active, drag to change block height -->
    <div
      class="resize-handle"
      :class="{ 'resize-handle--visible': isActive }"
      @mousedown.stop.prevent="startResize"
      title="Drag to change block height"
    >
      <div class="resize-handle-bar" />
      <span v-if="currentHeight" class="resize-handle-label">{{ currentHeight }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { IBlock } from '@/types/block'
import { useEditorStore } from '@/stores/editorStore'
import BlockRenderer from './BlockRenderer.vue'

const props = defineProps<{
  block: IBlock
  isActive: boolean
  isFirst: boolean
  isLast: boolean
}>()

defineEmits(['openContent', 'openSettings', 'moveUp', 'moveDown', 'duplicate', 'remove'])

const editorStore = useEditorStore()
const wrapperRef = ref<HTMLElement | null>(null)

// ── Resize state ─────────────────────────────────────────────────────────────
const resizing = ref(false)
const currentHeight = ref<string>('')
let startY = 0
let startHeight = 0

// Apply minHeight from settings so the saved height is reflected in the wrapper.
// Cover blocks also read this via their own computed style.
const wrapperStyle = computed(() => {
  const mh = props.block.settings.minHeight
  return mh ? { minHeight: mh } : {}
})

function selectBlock() {
  editorStore.setActiveBlock(props.block.id)
}

function startResize(e: MouseEvent) {
  resizing.value = true
  startY = e.clientY
  startHeight = wrapperRef.value?.getBoundingClientRect().height ?? 400
  currentHeight.value = Math.round(startHeight) + 'px'

  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'ns-resize'
}

function onResize(e: MouseEvent) {
  if (!resizing.value) return
  const delta = e.clientY - startY
  const newHeight = Math.max(80, Math.round(startHeight + delta))
  currentHeight.value = newHeight + 'px'
  // Live-update so block reflects the new height immediately
  editorStore.updateBlockSettings(props.block.id, { minHeight: newHeight + 'px' })
}

function stopResize() {
  resizing.value = false
  currentHeight.value = ''
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.userSelect = ''
  document.body.style.cursor = ''
}
</script>

<style scoped>
.block-wrapper {
  position: relative;
  cursor: pointer;
  transition: outline 0.15s;
}
.block-wrapper:hover {
  outline: 2px dashed rgba(25, 118, 210, 0.4);
  outline-offset: -2px;
}
.block-wrapper--active {
  outline: 2px solid #1976D2 !important;
  outline-offset: -2px;
}
.block-wrapper--resizing {
  outline: 2px solid #1976D2 !important;
  outline-offset: -2px;
  cursor: ns-resize;
}
.block-controls {
  position: absolute;
  top: -40px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  z-index: 50;
  padding: 4px 8px;
  background: rgba(25, 118, 210, 0.95);
  border-radius: 4px 4px 0 0;
}
.block-controls-left,
.block-controls-right {
  display: flex;
  gap: 4px;
  align-items: center;
}
.block-controls :deep(.v-btn) {
  color: #fff !important;
}

/* ── Resize handle ─────────────────────────────────────────────────────────── */
.resize-handle {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: ns-resize;
  z-index: 40;
  opacity: 0;
  transition: opacity 0.15s;
  gap: 8px;
}
.block-wrapper:hover .resize-handle,
.resize-handle--visible {
  opacity: 1 !important;
}
.resize-handle-bar {
  width: 48px;
  height: 4px;
  border-radius: 2px;
  background: #1976D2;
  pointer-events: none;
}
.resize-handle-label {
  font-size: 11px;
  font-weight: 600;
  color: #1976D2;
  background: rgba(255, 255, 255, 0.92);
  padding: 1px 6px;
  border-radius: 4px;
  pointer-events: none;
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
  min-width: 44px;
  text-align: center;
}
</style>
