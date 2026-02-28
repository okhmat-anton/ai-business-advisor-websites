<template>
  <!-- About: text left, image right -->
  <section class="about-block-01" :style="{ backgroundColor: settings.backgroundColor, padding: `${settings.paddingTop} 0 ${settings.paddingBottom}` }">
    <div class="about-container">
      <div class="about-text">
        <h2 :style="textStyle(content, 'title')">{{ content.title }}</h2>
        <p :style="textStyle(content, 'text', false)">{{ content.text }}</p>
      </div>
      <div class="about-image">
        <img :src="content.image" alt="About" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { textStyle } from '@/utils/textStyle'
defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
</script>

<style scoped>
.about-block-01 { width: 100%; }
.about-container { max-width: 1200px; margin: 0 auto; display: flex; gap: 60px; align-items: center; padding: 0 40px; }
.about-text { flex: 1; }
.about-text h2 { font-size: 36px; font-weight: 700; margin-bottom: 20px; color: #212121; }
.about-text p { font-size: 17px; line-height: 1.7; color: #555; }
.about-image { flex: 1; }
.about-image img { width: 100%; border-radius: 8px; object-fit: cover; }
@media (max-width: 768px) {
  .about-container { flex-direction: column; gap: 30px; }
}
</style>
