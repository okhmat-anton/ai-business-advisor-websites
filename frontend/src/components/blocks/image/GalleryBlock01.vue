<template>
  <section class="gallery-block-01" :style="{ backgroundColor: settings.backgroundColor, padding: `${settings.paddingTop} 0 ${settings.paddingBottom}` }">
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
defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
</script>

<style scoped>
.gallery-block-01 { width: 100%; }
.gallery-container { max-width: 1200px; margin: 0 auto; padding: 0 40px; }
.gallery-grid { display: grid; gap: 16px; }
.gallery-item img { width: 100%; border-radius: 6px; object-fit: cover; aspect-ratio: 4/3; }
</style>
