<template>
  <section class="form-block-01" :style="blockStyle">
    <div class="form-container">
      <h2 v-if="content.title" :style="textStyle(content, 'title')">{{ content.title }}</h2>
      <p v-if="content.subtitle" class="form-subtitle" :style="textStyle(content, 'subtitle', false)" v-html="content.subtitle" />
      <form class="form-fields" @submit.prevent="onSubmit">
        <div v-for="(field, i) in content.fields" :key="i" class="form-field">
          <label>{{ field.label }}</label>
          <textarea v-if="field.type === 'textarea'" :placeholder="field.placeholder" rows="4"></textarea>
          <input v-else :type="field.type" :placeholder="field.placeholder" />
        </div>
        <button type="submit" class="form-submit">{{ content.submitText || 'Submit' }}</button>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { textStyle } from '@/utils/textStyle'
import { useBlockStyle } from '@/composables/useBlockStyle'
const props = defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
const blockStyle = useBlockStyle(props.settings)

function onSubmit() {
  // Mock: just show alert
  alert('Form submitted (mock)')
}
</script>

<style scoped>
.form-block-01 { width: 100%; }
.form-container { max-width: 600px; margin: 0 auto; padding: 0 40px; text-align: center; }
@container (max-width: 768px) { .form-container { padding: 0 20px; } }
.form-container h2 { font-size: 32px; font-weight: 700; color: #212121; margin-bottom: 8px; }
.form-subtitle { color: #666; margin-bottom: 30px; }
.form-fields { display: flex; flex-direction: column; gap: 16px; text-align: left; }
.form-field label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 4px; color: #333; }
.form-field input, .form-field textarea { width: 100%; padding: 12px 16px; border: 1px solid #ddd; border-radius: 4px; font-size: 15px; box-sizing: border-box; }
.form-submit { margin-top: 8px; padding: 14px 40px; background: #1976D2; color: #fff; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; }
</style>
