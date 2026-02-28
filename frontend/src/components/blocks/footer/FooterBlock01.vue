<template>
  <footer class="footer-block-01" :style="{ backgroundColor: settings.backgroundColor, padding: `${settings.paddingTop} 0 ${settings.paddingBottom}` }">
    <div class="footer-container">
      <div v-if="content.socialLinks?.length" class="social-links">
        <a v-for="(link, i) in content.socialLinks" :key="i" :href="link.url">
          <v-icon>{{ link.icon }}</v-icon>
        </a>
      </div>
      <p class="copyright" :style="textStyle(content, 'copyright', false)">{{ content.copyright }}</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { textStyle } from '@/utils/textStyle'
defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
</script>

<style scoped>
.footer-block-01 { width: 100%; color: #fff; }
.footer-container { max-width: 1200px; margin: 0 auto; text-align: center; padding: 0 40px; }
.social-links { display: flex; gap: 20px; justify-content: center; margin-bottom: 16px; }
.social-links a { color: rgba(255,255,255,0.7); text-decoration: none; transition: color 0.2s; }
.social-links a:hover { color: #fff; }
.copyright { font-size: 14px; color: rgba(255,255,255,0.5); }
</style>
