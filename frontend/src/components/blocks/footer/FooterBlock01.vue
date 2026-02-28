<template>
  <footer class="footer-block-01" :style="footerStyle">
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
import { computed } from 'vue'
import { textStyle } from '@/utils/textStyle'
const props = defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()

const footerStyle = computed(() => {
  const s: Record<string, string> = {
    backgroundColor: props.settings.backgroundColor || '#1a1a2e',
    padding: `${props.settings.paddingTop} 0 ${props.settings.paddingBottom}`,
  }
  const img = props.settings.backgroundImage
  if (img) {
    s.backgroundImage = `url(${img})`
    s.backgroundSize = 'cover'
    s.backgroundPosition = 'center'
    if (props.settings.parallax) s.backgroundAttachment = 'fixed'
  }
  return s
})
</script>

<style scoped>
.footer-block-01 { width: 100%; color: #fff; }
.footer-container { max-width: 1200px; margin: 0 auto; text-align: center; padding: 0 40px; }
@container (max-width: 768px) { .footer-container { padding: 0 20px; } }
.social-links { display: flex; gap: 20px; justify-content: center; margin-bottom: 16px; }
.social-links a { color: rgba(255,255,255,0.7); text-decoration: none; transition: color 0.2s; }
.social-links a:hover { color: #fff; }
.copyright { font-size: 14px; color: rgba(255,255,255,0.5); }
</style>
