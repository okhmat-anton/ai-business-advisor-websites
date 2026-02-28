<template>
  <!-- Cover: centered with video background placeholder -->
  <div class="cover-block cover-block-03" :style="coverStyle">
    <div class="cover-overlay" :style="{ opacity: content.overlayOpacity || 0.4 }"></div>
    <div class="cover-content">
      <h1 class="cover-title" :style="textStyle(content, 'title')">{{ content.title }}</h1>
      <p class="cover-subtitle" :style="textStyle(content, 'subtitle')">{{ content.subtitle }}</p>
      <a v-if="content.buttonText" :href="content.buttonUrl || '#'" class="cover-btn">
        <v-icon left size="20">mdi-play-circle</v-icon>
        {{ content.buttonText }}
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { textStyle } from '@/utils/textStyle'

const props = defineProps<{
  content: Record<string, any>
  settings: Record<string, any>
}>()

const coverStyle = computed(() => ({
  backgroundImage: `url(${props.settings.backgroundImage || props.content.backgroundImage || ''})`,
  backgroundColor: props.settings.backgroundColor || '#16213e',
  minHeight: props.settings.minHeight || '100vh',
}))
</script>

<style scoped>
.cover-block-03 {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background-size: cover;
  background-position: center;
  color: #fff;
}
.cover-overlay { position: absolute; inset: 0; background: #000; }
.cover-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 700px;
  padding: 40px 20px;
}
.cover-title { font-size: 52px; font-weight: 700; margin-bottom: 16px; }
.cover-subtitle { font-size: 20px; margin-bottom: 32px; opacity: 0.9; }
.cover-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 36px;
  border: 2px solid #fff;
  color: #fff;
  text-decoration: none;
  font-weight: 600;
  border-radius: 4px;
  transition: background 0.2s;
}
.cover-btn:hover { background: rgba(255,255,255,0.15); }
</style>
