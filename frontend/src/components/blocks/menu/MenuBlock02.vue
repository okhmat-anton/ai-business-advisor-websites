<template>
  <nav class="menu-block-02" :style="{ backgroundColor: settings.backgroundColor }">
    <div class="menu-container">
      <div class="menu-logo">{{ content.logo }}</div>
      <div class="menu-links">
        <a v-for="(link, i) in content.links" :key="i" :href="link.url">{{ link.text }}</a>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
</script>

<style scoped>
.menu-block-02 { width: 100%; position: absolute; top: 0; left: 0; right: 0; z-index: 100; }
.menu-container { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; padding: 20px 40px; }
.menu-logo { font-size: 22px; font-weight: 700; color: #fff; }
.menu-links { display: flex; gap: 28px; margin-left: auto; }
.menu-links a { text-decoration: none; color: rgba(255,255,255,0.85); font-size: 15px; font-weight: 500; }
.menu-links a:hover { color: #fff; }
</style>
