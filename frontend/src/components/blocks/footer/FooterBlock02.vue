<template>
  <footer class="footer-block-02" :style="{ backgroundColor: settings.backgroundColor, padding: `${settings.paddingTop} 0 ${settings.paddingBottom}` }">
    <div class="footer-container">
      <div class="footer-top">
        <div class="footer-brand">
          <h3 :style="textStyle(content, 'logo')">{{ content.logo }}</h3>
          <p :style="textStyle(content, 'description', false)" v-html="content.description" />
        </div>
        <div v-for="(col, i) in content.columns" :key="i" class="footer-column">
          <h4>{{ col.title }}</h4>
          <ul>
            <li v-for="(link, j) in col.links" :key="j">
              <a :href="link.url">{{ link.text }}</a>
            </li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p :style="textStyle(content, 'copyright', false)">{{ content.copyright }}</p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { textStyle } from '@/utils/textStyle'
defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
</script>

<style scoped>
.footer-block-02 { width: 100%; color: #fff; }
.footer-container { max-width: 1200px; margin: 0 auto; padding: 0 40px; }
.footer-top { display: flex; gap: 60px; margin-bottom: 40px; }
.footer-brand { flex: 1.5; }
.footer-brand h3 { font-size: 22px; margin-bottom: 8px; }
.footer-brand p { color: rgba(255,255,255,0.6); font-size: 14px; line-height: 1.6; }
.footer-column { flex: 1; }
.footer-column h4 { font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; color: rgba(255,255,255,0.8); }
.footer-column ul { list-style: none; padding: 0; }
.footer-column li { margin-bottom: 10px; }
.footer-column a { color: rgba(255,255,255,0.5); text-decoration: none; font-size: 14px; }
.footer-column a:hover { color: #fff; }
.footer-bottom { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; }
.footer-bottom p { font-size: 13px; color: rgba(255,255,255,0.4); }
@media (max-width: 768px) { .footer-top { flex-direction: column; gap: 30px; } }
</style>
