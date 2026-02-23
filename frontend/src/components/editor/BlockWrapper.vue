<template>
  <!-- Wrapper around each block in edit mode with control buttons -->
  <div
    class="block-wrapper"
    :class="{ 'block-wrapper--active': isActive }"
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
  </div>
</template>

<script setup lang="ts">
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

function selectBlock() {
  editorStore.setActiveBlock(props.block.id)
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
</style>
