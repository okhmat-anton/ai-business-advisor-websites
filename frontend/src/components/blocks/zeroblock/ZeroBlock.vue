<template>
  <!-- Zero Block: free positioning canvas -->
  <section class="zero-block" :style="{ backgroundColor: settings.backgroundColor, height: content.height || '600px', position: 'relative' }">
    <div v-for="el in content.elements" :key="el.id" class="zero-element"
      :style="getElementStyle(el)">
      <template v-if="el.type === 'text'">
        <div v-html="el.content.html || el.content.text"></div>
      </template>
      <template v-else-if="el.type === 'image'">
        <img :src="el.content.src" :alt="el.content.alt || ''" style="width:100%;height:100%;object-fit:cover;" />
      </template>
      <template v-else-if="el.type === 'shape'">
        <div :style="{ width: '100%', height: '100%', backgroundColor: el.content.color || '#1976D2', borderRadius: el.content.borderRadius || '0' }"></div>
      </template>
      <template v-else-if="el.type === 'button'">
        <a :href="el.content.url || '#'" class="zero-btn">{{ el.content.text }}</a>
      </template>
    </div>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()

// Use desktop positioning by default
function getElementStyle(el: any) {
  const pos = el.position?.desktop || { x: 0, y: 0, width: 100, height: 50, zIndex: 1 }
  return {
    position: 'absolute' as const,
    left: `${pos.x}px`,
    top: `${pos.y}px`,
    width: `${pos.width}px`,
    height: `${pos.height}px`,
    zIndex: pos.zIndex,
  }
}
</script>

<style scoped>
.zero-block { width: 100%; overflow: hidden; }
.zero-element { transition: none; }
.zero-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: #1976D2;
  color: #fff;
  text-decoration: none;
  font-weight: 600;
  border-radius: 4px;
}
</style>
