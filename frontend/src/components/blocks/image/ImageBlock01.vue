<template>
  <section class="image-block-01" :style="blockStyle">
    <div class="image-container">
      <img :src="content.image" :alt="content.alt || ''" />
      <p v-if="content.caption" class="caption" :style="textStyle(content, 'caption', false)">{{ content.caption }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { textStyle } from '@/utils/textStyle'
import { useBlockStyle } from '@/composables/useBlockStyle'
const props = defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
const blockStyle = useBlockStyle(props.settings)
</script>

<style scoped>
.image-block-01 { width: 100%; }
.image-container { max-width: 1000px; margin: 0 auto; padding: 0 40px; }
.image-container img { width: 100%; border-radius: 8px; }
.caption { font-size: 14px; color: #888; margin-top: 12px; }
</style>
