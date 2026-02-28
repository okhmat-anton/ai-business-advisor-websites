<template>
  <!-- Cover: left-aligned text -->
  <div class="cover-block cover-block-02" :style="coverStyle">
    <div class="cover-overlay" :style="{ opacity: content.overlayOpacity || 0.6 }"></div>
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
  backgroundColor: props.settings.backgroundColor || '#0f3460',
  minHeight: props.settings.minHeight || '100vh',
}))
</script>

<style scoped>
.cover-block-02 {
  position: relative;
  display: flex;
  align-items: center;
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
  max-width: 600px;
  padding: 40px 80px;
}
.cover-title {
  font-size: 52px;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}
.cover-subtitle {
  font-size: 20px;
  margin-bottom: 32px;
  opacity: 0.85;
}
.cover-btn {
  display: inline-block;
  padding: 14px 36px;
  background: #fff;
  color: #0f3460;
  text-decoration: none;
  font-weight: 600;
  border-radius: 4px;
}
</style>
