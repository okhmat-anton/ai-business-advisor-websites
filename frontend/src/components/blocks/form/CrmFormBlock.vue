<template>
  <section
    class="crm-form-block"
    :style="{
      backgroundColor: settings.backgroundColor,
      paddingTop: settings.paddingTop,
      paddingBottom: settings.paddingBottom,
    }"
  >
    <div class="crm-form-inner">
      <h2 v-if="content.title" class="crm-form-title" :style="textStyle(content, 'title')">{{ content.title }}</h2>
      <p v-if="content.subtitle" class="crm-form-subtitle" :style="textStyle(content, 'subtitle', false)" v-html="content.subtitle" />

      <!-- Embed container: scripts are executed via DOM injection on mount -->
      <div v-if="content.embedCode" ref="embedContainer" class="crm-form-embed" />

      <!-- Placeholder when no form selected -->
      <div v-else class="crm-form-placeholder">
        <div class="crm-form-placeholder-inner">
          <v-icon size="40" color="grey-lighten-1">mdi-form-select</v-icon>
          <p class="text-body-2 text-grey mt-2">No CRM form selected</p>
          <p class="text-caption text-grey">Click "Edit Content" and choose a form</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import { textStyle } from '@/utils/textStyle'

const props = defineProps<{ content: Record<string, any>; settings: Record<string, any> }>()

const embedContainer = ref<HTMLElement | null>(null)

/**
 * Inject embed HTML into the container and re-execute any <script> tags.
 * Vue's v-html silently drops scripts – this workaround creates real DOM nodes
 * so that third-party form scripts actually run.
 */
function injectEmbed(html: string) {
  const el = embedContainer.value
  if (!el) return

  // Clear previous content
  el.innerHTML = ''

  // Create a document fragment from the HTML string
  const fragment = document.createRange().createContextualFragment(html)
  el.appendChild(fragment)
}

onMounted(() => {
  if (props.content.embedCode) {
    nextTick(() => injectEmbed(props.content.embedCode))
  }
})

// Re-inject when embedCode changes (user selects different form)
watch(
  () => props.content.embedCode,
  (code) => {
    if (code) {
      nextTick(() => injectEmbed(code))
    } else if (embedContainer.value) {
      embedContainer.value.innerHTML = ''
    }
  }
)
</script>

<style scoped>
.crm-form-block {
  width: 100%;
}

.crm-form-inner {
  max-width: 640px;
  margin: 0 auto;
  padding: 0 40px;
  text-align: center;
}

.crm-form-title {
  font-size: 28px;
  font-weight: 700;
  color: #212121;
  margin-bottom: 8px;
}

.crm-form-subtitle {
  color: #666;
  margin-bottom: 24px;
  font-size: 16px;
}

.crm-form-embed {
  text-align: left;
}

.crm-form-placeholder {
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  padding: 40px 20px;
}

.crm-form-placeholder-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>
