<template>
  <!-- Editor canvas: the main editing area with all blocks -->
  <div class="editor-canvas" :style="{ ...canvasStyle, ...fontVars }" @click.self="deselectBlock">
    <!-- Empty state -->
    <div v-if="!sortedBlocks.length" class="empty-state">
      <v-icon size="64" color="grey-lighten-1">mdi-plus-circle-outline</v-icon>
      <h3>Page is empty</h3>
      <p>Click the button below to add your first block</p>
      <v-btn color="primary" @click="uiStore.openBlocksLibrary()">
        <v-icon left>mdi-plus</v-icon>
        Add Block
      </v-btn>
    </div>

    <!-- Blocks list -->
    <div v-else class="blocks-list">
      <!-- Add button at the top -->
      <BlockAddButton />

      <template v-for="(block, index) in sortedBlocks" :key="block.id">
        <BlockWrapper
          :block="block"
          :is-active="block.id === editorStore.activeBlockId"
          :is-first="index === 0"
          :is-last="index === sortedBlocks.length - 1"
          @open-content="openContent(block.id)"
          @open-settings="openSettings(block.id)"
          @move-up="editorStore.moveBlockUp(block.id)"
          @move-down="editorStore.moveBlockDown(block.id)"
          @duplicate="editorStore.duplicateBlock(block.id)"
          @remove="editorStore.removeBlock(block.id)"
        />
        <BlockAddButton :after-block-id="block.id" />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useEditorStore } from '@/stores/editorStore'
import { useUiStore } from '@/stores/uiStore'
import { useSiteStore } from '@/stores/siteStore'
import { useResponsive } from '@/composables/useResponsive'
import BlockWrapper from './BlockWrapper.vue'
import BlockAddButton from './BlockAddButton.vue'

const editorStore = useEditorStore()
const uiStore = useUiStore()
const siteStore = useSiteStore()
const { currentWidth, currentDevice } = useResponsive()

const sortedBlocks = computed(() => editorStore.sortedBlocks)

// Inject CSS custom properties for site fonts so all block components can use them
const fontVars = computed(() => {
  const fonts = siteStore.currentSite?.globalSettings?.fonts as Record<string, string> | undefined
  return {
    '--font-heading': fonts?.heading ? `"${fonts.heading}", sans-serif` : 'inherit',
    '--font-body': fonts?.body ? `"${fonts.body}", sans-serif` : 'inherit',
    // Compensate for the 64px editor toolbar so 100vh-based cover heights
    // match the published page where there is no toolbar offset.
    '--cover-vh': 'calc(100vh - 64px)',
  }
})

const canvasStyle = computed(() => {
  if (currentDevice.value === 'desktop') {
    return { maxWidth: '100%' }
  }
  return {
    maxWidth: `${currentWidth.value}px`,
    margin: '0 auto',
    boxShadow: '0 0 20px rgba(0,0,0,0.1)',
  }
})

function deselectBlock() {
  editorStore.setActiveBlock(null)
  uiStore.closeAllPanels()
}

function openContent(blockId: string) {
  editorStore.setActiveBlock(blockId)
  uiStore.openContentPanel()
}

function openSettings(blockId: string) {
  editorStore.setActiveBlock(blockId)
  uiStore.openSettingsPanel()
}
</script>

<style scoped>
.editor-canvas {
  min-height: calc(100vh - 64px);
  background: #f5f5f5;
  transition: max-width 0.3s;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 12px;
  color: #999;
}
.empty-state h3 { font-size: 20px; color: #666; }
.empty-state p { font-size: 14px; margin-bottom: 8px; }
.blocks-list {
  background: #fff;
}
</style>
