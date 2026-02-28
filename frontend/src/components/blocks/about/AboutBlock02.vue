<template>
  <!-- About: description with counters -->
  <section class="about-block-02" :style="blockStyle">
    <div class="about-container">
      <h2 :style="textStyle(content, 'title')">{{ content.title }}</h2>
      <p class="about-desc" :style="textStyle(content, 'text', false)" v-html="content.text" />
      <div class="counters">
        <div v-for="(counter, i) in content.counters" :key="i" class="counter-item">
          <span class="counter-value">{{ counter.value }}</span>
          <span class="counter-label">{{ counter.label }}</span>
        </div>
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
.about-block-02 { width: 100%; }
.about-container { max-width: 1000px; margin: 0 auto; text-align: center; padding: 0 40px; }
.about-container h2 { font-size: 36px; font-weight: 700; margin-bottom: 16px; color: #212121; }
.about-desc { font-size: 18px; color: #666; max-width: 700px; margin: 0 auto 50px; line-height: 1.6; }
.counters { display: flex; justify-content: center; gap: 60px; flex-wrap: wrap; }
.counter-item { display: flex; flex-direction: column; align-items: center; }
.counter-value { font-size: 42px; font-weight: 700; color: #1976D2; }
.counter-label { font-size: 14px; color: #888; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }
@container (max-width: 768px) {
  .about-container { padding: 0 20px; }
  .about-container h2 { font-size: 26px; }
  .counters { gap: 30px; }
  .counter-value { font-size: 32px; }
}
</style>
