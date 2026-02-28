<template>
  <section class="form-block-02" :style="blockStyle">
    <div class="subscribe-container">
      <h2 :style="textStyle(content, 'title')">{{ content.title }}</h2>
      <p :style="textStyle(content, 'subtitle', false)" v-html="content.subtitle" />
      <form class="subscribe-form" @submit.prevent="onSubmit">
        <input type="email" :placeholder="content.placeholder || 'Enter your email'" />
        <button type="submit">{{ content.submitText || 'Subscribe' }}</button>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { textStyle } from '@/utils/textStyle'
import { useBlockStyle } from '@/composables/useBlockStyle'
const props = defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()
const blockStyle = useBlockStyle(props.settings)
function onSubmit() { alert('Subscribed (mock)') }
</script>

<style scoped>
.form-block-02 { width: 100%; color: #fff; }
.subscribe-container { max-width: 600px; margin: 0 auto; text-align: center; padding: 0 40px; }
.subscribe-container h2 { font-size: 32px; font-weight: 700; margin-bottom: 8px; }
.subscribe-container p { opacity: 0.8; margin-bottom: 24px; }
.subscribe-form { display: flex; gap: 8px; }
.subscribe-form input { flex: 1; padding: 14px 16px; border: 1px solid rgba(255,255,255,0.3); background: rgba(255,255,255,0.1); color: #fff; border-radius: 4px; font-size: 15px; }
.subscribe-form input::placeholder { color: rgba(255,255,255,0.5); }
.subscribe-form button { padding: 14px 28px; background: #fff; color: #1a1a2e; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; }
@container (max-width: 480px) { .subscribe-container { padding: 0 20px; } .subscribe-form { flex-direction: column; } }
</style>
