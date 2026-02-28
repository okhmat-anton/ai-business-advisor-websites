<template>
  <!-- Cover: full-width with centered text overlay -->
  <div class="cover-block cover-block-01" :style="coverStyle">
    <div class="cover-overlay" :style="{ opacity: content.overlayOpacity || 0.5 }"></div>
    <div class="cover-content">
      <h1 class="cover-title" :style="textStyle(content, 'title')">{{ content.title }}</h1>
      <p class="cover-subtitle" :style="textStyle(content, 'subtitle')">{{ content.subtitle }}</p>
      <a v-if="content.buttonText" :href="content.buttonUrl || '#'" class="cover-btn">
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
  backgroundColor: props.settings.backgroundColor || '#1a1a2e',
  // minHeight from settings (set by resize handle or SettingsPanel), default full viewport
  minHeight: props.settings.minHeight || '100vh',
}))
</script>

<style scoped>
.cover-block-01 {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background-size: cover;
  background-position: center;
  color: #fff;
}
.cover-overlay {
  position: absolute;
  inset: 0;
  background: #000;
}
.cover-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 800px;
  padding: 40px 20px;
}
.cover-title {
  font-size: 56px;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}
.cover-subtitle {
  font-size: 22px;
  margin-bottom: 32px;
  opacity: 0.9;
}
.cover-btn {
  display: inline-block;
  padding: 14px 40px;
  background: #fff;
  color: #1a1a2e;
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
  border-radius: 4px;
  transition: transform 0.2s;
}
.cover-btn:hover {
  transform: translateY(-2px);
}
</style>
