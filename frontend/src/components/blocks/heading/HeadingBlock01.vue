<template>
  <section class="heading-block-01" :style="{ backgroundColor: settings.backgroundColor, padding: `${settings.paddingTop} 0 ${settings.paddingBottom}`, textAlign: settings.align }">
    <div class="heading-container">
      <component :is="content.level || 'h2'" class="heading-title" :style="textStyle(content, 'title')">{{ content.title }}</component>
      <p v-if="content.subtitle" class="heading-subtitle" :style="textStyle(content, 'subtitle')">{{ content.subtitle }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { textStyle } from '@/utils/textStyle'
defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
</script>

<style scoped>
.heading-block-01 { width: 100%; }
.heading-container { max-width: 900px; margin: 0 auto; padding: 0 40px; }
.heading-title { font-size: 40px; font-weight: 700; color: #212121; margin-bottom: 8px; }
.heading-subtitle { font-size: 18px; color: #888; }
</style>
