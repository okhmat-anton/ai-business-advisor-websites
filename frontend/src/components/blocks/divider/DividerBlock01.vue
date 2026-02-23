<template>
  <section class="divider-block-01" :style="{ backgroundColor: settings.backgroundColor, padding: `${settings.paddingTop} 0 ${settings.paddingBottom}`, textAlign: settings.align }">
    <hr :style="{ borderStyle: content.style || 'solid', width: content.width || '100px', borderColor: content.color || '#dee2e6' }" />
  </section>
</template>

<script setup lang="ts">
defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
</script>

<style scoped>
.divider-block-01 { width: 100%; }
.divider-block-01 hr { border: none; border-top-width: 1px; margin: 0 auto; }
</style>
