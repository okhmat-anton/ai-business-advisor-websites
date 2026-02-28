<template>
  <section class="columns-block-01" :style="blockStyle">
    <div class="columns-container">
      <h2 v-if="content.title" class="columns-title" :style="textStyle(content, 'title')">{{ content.title }}</h2>
      <div class="cards-grid">
        <div v-for="(card, i) in content.cards" :key="i" class="card-item">
          <v-icon size="48" color="#1976D2">{{ card.icon }}</v-icon>
          <h3>{{ card.title }}</h3>
          <p>{{ card.text }}</p>
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
.columns-block-01 { width: 100%; }
.columns-container { max-width: 1200px; margin: 0 auto; padding: 0 40px; }
.columns-title { font-size: 36px; font-weight: 700; text-align: center; margin-bottom: 50px; color: #212121; }
.cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 40px; }
.card-item { text-align: center; padding: 30px 20px; }
.card-item h3 { font-size: 20px; font-weight: 700; margin: 16px 0 10px; color: #212121; }
.card-item p { font-size: 15px; line-height: 1.6; color: #666; }
</style>
