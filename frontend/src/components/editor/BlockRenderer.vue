<template>
  <!-- Dynamic block renderer: resolves block type to Vue component -->
  <component
    v-if="blockComponent"
    :is="blockComponent"
    :content="block.content"
    :settings="block.settings"
  />
  <div v-else class="unknown-block">
    <v-icon>mdi-alert-circle-outline</v-icon>
    <span>Unknown block type: {{ block.type }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { IBlock } from '@/types/block'
import { getBlockComponent } from '@/utils/blockRegistry'

const props = defineProps<{ block: IBlock }>()

const blockComponent = computed(() => getBlockComponent(props.block.type))
</script>

<style scoped>
.unknown-block {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: #fff3cd;
  color: #856404;
  border: 1px dashed #ffc107;
  border-radius: 4px;
  margin: 8px 0;
}
</style>
