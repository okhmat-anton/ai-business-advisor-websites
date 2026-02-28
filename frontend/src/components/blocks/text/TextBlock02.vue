<template>
  <section class="text-block-02" :style="blockStyle">
    <div class="text-container">
      <h2 v-if="content.title" :style="textStyle(content, 'title')">{{ content.title }}</h2>
      <div class="two-columns">
        <div :style="textStyle(content, 'leftText', false)" v-html="content.leftText" />
        <div :style="textStyle(content, 'rightText', false)" v-html="content.rightText" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { textStyle } from '@/utils/textStyle'
import { useBlockStyle } from '@/composables/useBlockStyle'
const props = defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
const blockStyle = useBlockStyle(props.settings)
</script>

<style scoped>
.text-block-02 { width: 100%; }
.text-container { max-width: 1100px; margin: 0 auto; padding: 0 40px; }
.text-container h2 { font-size: 32px; font-weight: 700; margin-bottom: 30px; color: #212121; text-align: center; }
.two-columns { display: flex; gap: 40px; }
.two-columns p { flex: 1; font-size: 16px; line-height: 1.7; color: #555; }
@media (max-width: 768px) { .two-columns { flex-direction: column; } }
</style>
