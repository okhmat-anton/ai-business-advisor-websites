<template>
  <section class="button-block-01" :style="blockStyle">
    <div class="button-container">
      <a v-for="(btn, i) in content.buttons" :key="i" :href="btn.url || '#'"
         :class="['btn', `btn-${btn.style || 'primary'}`]">
        {{ btn.text }}
      </a>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useBlockStyle } from '@/composables/useBlockStyle'
const props = defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
const blockStyle = useBlockStyle(props.settings)
</script>

<style scoped>
.button-block-01 { width: 100%; }
.button-container { display: flex; gap: 16px; justify-content: center; padding: 0 40px; flex-wrap: wrap; }
.btn { display: inline-block; padding: 14px 36px; text-decoration: none; font-weight: 600; border-radius: 4px; font-size: 16px; transition: transform 0.2s; }
.btn:hover { transform: translateY(-2px); }
.btn-primary { background: #1976D2; color: #fff; }
.btn-outlined { background: transparent; color: #1976D2; border: 2px solid #1976D2; }
</style>
