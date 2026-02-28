<template>
  <nav class="menu-block-01" :style="{ backgroundColor: settings.backgroundColor }">
    <div class="menu-container">
      <div class="menu-logo" :style="textStyle(content, 'logo')">{{ content.logo }}</div>
      <div class="menu-links">
        <a v-for="(link, i) in content.links" :key="i" :href="link.url">{{ link.text }}</a>
      </div>
      <a v-if="content.ctaButton" :href="content.ctaButton.url" class="menu-cta">
        {{ content.ctaButton.text }}
      </a>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { textStyle } from '@/utils/textStyle'
defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
</script>

<style scoped>
.menu-block-01 { width: 100%; position: sticky; top: 0; z-index: 100; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.menu-container { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; padding: 14px 40px; gap: 32px; }
.menu-logo { font-size: 22px; font-weight: 700; color: #212121; }
.menu-links { display: flex; gap: 24px; flex: 1; justify-content: center; }
.menu-links a { text-decoration: none; color: #555; font-size: 15px; font-weight: 500; transition: color 0.2s; }
.menu-links a:hover { color: #1976D2; }
.menu-cta { padding: 8px 24px; background: #1976D2; color: #fff; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 14px; white-space: nowrap; }
@container (max-width: 768px) {
  .menu-links { display: none; }
}
</style>
