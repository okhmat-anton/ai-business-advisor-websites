<template>
  <section class="gallery-block-01" :style="blockStyle">
    <div class="gallery-container">
      <div class="gallery-grid" :style="{ gridTemplateColumns: `repeat(${content.columns || 2}, 1fr)` }">
        <div v-for="(img, i) in content.images" :key="i" class="gallery-item">
          <img :src="img.src" :alt="img.alt || ''" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useBlockStyle } from '@/composables/useBlockStyle'
const props = defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
const blockStyle = useBlockStyle(props.settings)
</script>

<style scoped>
.gallery-block-01 { width: 100%; }
.gallery-container { max-width: 1200px; margin: 0 auto; padding: 0 40px; }
.gallery-grid { display: grid; gap: 16px; }
.gallery-item img { width: 100%; border-radius: 6px; object-fit: cover; aspect-ratio: 4/3; }
</style>
