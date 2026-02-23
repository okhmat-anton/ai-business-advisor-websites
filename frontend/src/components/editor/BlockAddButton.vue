<template>
  <!-- "+" button between blocks to insert a new block -->
  <div class="block-add-btn" @click="openLibrary">
    <v-btn icon size="small" color="primary" variant="tonal">
      <v-icon>mdi-plus</v-icon>
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/uiStore'

const props = defineProps<{ afterBlockId?: string }>()
const uiStore = useUiStore()

function openLibrary() {
  uiStore.openBlocksLibrary(props.afterBlockId)
}
</script>

<style scoped>
.block-add-btn {
  display: flex;
  justify-content: center;
  padding: 6px 0;
  opacity: 0;
  transition: opacity 0.2s;
}
.block-add-btn:hover {
  opacity: 1;
}
/* Always show when parent is hovered */
:hover > .block-add-btn,
.block-add-btn:focus-within {
  opacity: 1;
}
</style>
