<template>
  <section class="video-block-01" :style="{ backgroundColor: settings.backgroundColor, padding: `${settings.paddingTop} 0 ${settings.paddingBottom}` }">
    <div class="video-container">
      <h2 v-if="content.title" class="video-title">{{ content.title }}</h2>
      <div class="video-wrapper" :style="{ aspectRatio: content.aspectRatio || '16/9' }">
        <iframe :src="content.videoUrl" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
</script>

<style scoped>
.video-block-01 { width: 100%; }
.video-container { max-width: 900px; margin: 0 auto; padding: 0 40px; text-align: center; }
.video-title { font-size: 28px; color: #fff; margin-bottom: 24px; }
.video-wrapper { width: 100%; border-radius: 8px; overflow: hidden; }
.video-wrapper iframe { width: 100%; height: 100%; }
</style>
