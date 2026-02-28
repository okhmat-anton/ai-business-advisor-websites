<template>
  <section class="text-block-01" :style="{ backgroundColor: settings.backgroundColor, padding: `${settings.paddingTop} 0 ${settings.paddingBottom}`, textAlign: settings.align }">
    <div class="text-container">
      <h2 v-if="content.title" :style="textStyle(content, 'title')">{{ content.title }}</h2>
      <p :style="textStyle(content, 'text', false)" v-html="content.text" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { textStyle } from '@/utils/textStyle'
defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
</script>

<style scoped>
.text-block-01 { width: 100%; }
.text-container { max-width: 800px; margin: 0 auto; padding: 0 40px; }
.text-container h2 { font-size: 32px; font-weight: 700; margin-bottom: 20px; color: #212121; }
.text-container p { font-size: 17px; line-height: 1.8; color: #555; }
</style>
