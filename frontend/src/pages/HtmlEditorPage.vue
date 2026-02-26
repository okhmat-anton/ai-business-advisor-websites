<template>
  <v-app>
    <!-- Toolbar -->
    <div class="html-editor-toolbar">
      <v-btn icon variant="text" size="small" @click="goBack">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <span class="text-subtitle-2 mx-2">{{ pageTitle }}</span>

      <v-chip size="x-small" color="warning" variant="tonal" class="mr-2">HTML</v-chip>

      <v-spacer />

      <!-- Device preview toggle -->
      <v-btn-toggle v-model="deviceMode" density="compact" variant="outlined" divided mandatory class="mr-3">
        <v-btn value="desktop" size="small"><v-icon size="18">mdi-monitor</v-icon></v-btn>
        <v-btn value="tablet" size="small"><v-icon size="18">mdi-tablet</v-icon></v-btn>
        <v-btn value="mobile" size="small"><v-icon size="18">mdi-cellphone</v-icon></v-btn>
      </v-btn-toggle>

      <!-- Layout toggle -->
      <v-btn-toggle v-model="layout" density="compact" variant="outlined" divided mandatory class="mr-3">
        <v-btn value="split" size="small">
          <v-icon size="18">mdi-view-split-vertical</v-icon>
          <v-tooltip activator="parent" location="bottom">Split view</v-tooltip>
        </v-btn>
        <v-btn value="code" size="small">
          <v-icon size="18">mdi-code-tags</v-icon>
          <v-tooltip activator="parent" location="bottom">Code only</v-tooltip>
        </v-btn>
        <v-btn value="preview" size="small">
          <v-icon size="18">mdi-eye</v-icon>
          <v-tooltip activator="parent" location="bottom">Preview only</v-tooltip>
        </v-btn>
      </v-btn-toggle>

      <v-btn
        variant="tonal"
        size="small"
        color="primary"
        :loading="isSaving"
        :disabled="!isDirty"
        prepend-icon="mdi-content-save"
        @click="save"
        class="mr-2"
      >
        Save
      </v-btn>
    </div>

    <!-- Editor body -->
    <div class="html-editor-body" :class="`layout-${layout}`">
      <!-- Code editor panel -->
      <div v-show="layout !== 'preview'" class="code-panel">
        <div class="code-panel-header">
          <v-icon size="16" class="mr-1">mdi-code-tags</v-icon>
          <span class="text-caption font-weight-medium">HTML Source</span>
          <v-spacer />
          <v-btn variant="text" size="x-small" @click="formatHtml" title="Format HTML">
            <v-icon size="16">mdi-auto-fix</v-icon>
          </v-btn>
          <v-btn variant="text" size="x-small" @click="copyHtml" title="Copy to clipboard">
            <v-icon size="16">mdi-content-copy</v-icon>
          </v-btn>
        </div>
        <textarea
          ref="codeEditor"
          v-model="htmlCode"
          class="code-textarea"
          spellcheck="false"
          wrap="off"
          @input="onCodeChange"
          @keydown.tab.prevent="insertTab"
        />
      </div>

      <!-- Preview panel -->
      <div v-show="layout !== 'code'" class="preview-panel">
        <div class="preview-panel-header">
          <v-icon size="16" class="mr-1">mdi-eye</v-icon>
          <span class="text-caption font-weight-medium">Live Preview</span>
          <v-spacer />
          <v-btn variant="text" size="x-small" @click="refreshPreview" title="Refresh preview">
            <v-icon size="16">mdi-refresh</v-icon>
          </v-btn>
        </div>
        <div class="preview-container" :style="previewContainerStyle">
          <iframe
            ref="previewIframe"
            :srcdoc="previewHtml"
            class="preview-iframe"
            sandbox="allow-scripts allow-same-origin"
            frameborder="0"
          />
        </div>
      </div>
    </div>

    <!-- Snackbar -->
    <v-snackbar v-model="showSnackbar" :color="snackbarColor" timeout="2000" location="bottom right">
      {{ snackbarText }}
    </v-snackbar>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSiteStore } from '@/stores/siteStore'
import { DEVICE_SIZES } from '@/types/editor'

const route = useRoute()
const router = useRouter()
const siteStore = useSiteStore()

// State
const htmlCode = ref('')
const originalHtml = ref('')
const isDirty = ref(false)
const isSaving = ref(false)
const deviceMode = ref('desktop')
const layout = ref<'split' | 'code' | 'preview'>('split')

// Refs
const codeEditor = ref<HTMLTextAreaElement | null>(null)
const previewIframe = ref<HTMLIFrameElement | null>(null)

// Snackbar
const showSnackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

// Computed
const pageTitle = computed(() => siteStore.currentPage?.title || 'HTML Page')

const previewHtml = ref('')

// Debounced preview update
let previewTimeout: ReturnType<typeof setTimeout> | null = null

const previewContainerStyle = computed(() => {
  const sizes = DEVICE_SIZES[deviceMode.value as keyof typeof DEVICE_SIZES]
  return {
    maxWidth: sizes ? `${sizes.width}px` : '100%',
    margin: '0 auto',
  }
})

function onCodeChange() {
  isDirty.value = htmlCode.value !== originalHtml.value

  // Debounced preview update (300ms)
  if (previewTimeout) clearTimeout(previewTimeout)
  previewTimeout = setTimeout(() => {
    previewHtml.value = htmlCode.value
  }, 300)
}

function refreshPreview() {
  previewHtml.value = ''
  setTimeout(() => {
    previewHtml.value = htmlCode.value
  }, 50)
}

function insertTab(e: KeyboardEvent) {
  const textarea = e.target as HTMLTextAreaElement
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  htmlCode.value = htmlCode.value.substring(0, start) + '  ' + htmlCode.value.substring(end)
  // Restore cursor position
  setTimeout(() => {
    textarea.selectionStart = textarea.selectionEnd = start + 2
  }, 0)
  onCodeChange()
}

function formatHtml() {
  // Simple HTML formatting: indent nested tags
  try {
    let formatted = htmlCode.value
    // Basic formatting: add newlines after closing tags and before opening tags
    formatted = formatted
      .replace(/>\s*</g, '>\n<')
      .replace(/(<[^/][^>]*>)\n/g, '$1\n')

    // Re-indent
    const lines = formatted.split('\n')
    let indent = 0
    const result: string[] = []
    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed) continue
      // Decrease indent for closing tags
      if (trimmed.startsWith('</')) indent = Math.max(0, indent - 1)
      result.push('  '.repeat(indent) + trimmed)
      // Increase indent for opening tags (not self-closing)
      if (trimmed.match(/^<[^/!][^>]*[^/]>/) && !trimmed.match(/^<(br|hr|img|input|meta|link)/i)) {
        indent++
      }
    }
    htmlCode.value = result.join('\n')
    onCodeChange()
    notify('HTML formatted', 'success')
  } catch {
    notify('Format failed', 'error')
  }
}

async function copyHtml() {
  try {
    await navigator.clipboard.writeText(htmlCode.value)
    notify('Copied to clipboard', 'success')
  } catch {
    notify('Copy failed', 'error')
  }
}

async function save() {
  if (!siteStore.currentSite || !siteStore.currentPage) return
  isSaving.value = true
  try {
    await siteStore.savePage(siteStore.currentSite.id, {
      ...siteStore.currentPage,
      htmlContent: htmlCode.value,
    })
    originalHtml.value = htmlCode.value
    isDirty.value = false
    notify('Page saved', 'success')
  } catch (err: any) {
    notify(`Save failed: ${err.message || 'Unknown error'}`, 'error')
  } finally {
    isSaving.value = false
  }
}

function goBack() {
  const siteId = route.params.siteId as string
  router.push(`/sites/${siteId}`)
}

function notify(text: string, color = 'success') {
  snackbarText.value = text
  snackbarColor.value = color
  showSnackbar.value = true
}

// Keyboard shortcuts
function onKeyDown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 's') {
    e.preventDefault()
    if (isDirty.value) save()
  }
}

onMounted(async () => {
  const siteId = route.params.siteId as string
  const pageId = route.params.pageId as string

  if (siteId && !siteStore.currentSite) {
    await siteStore.loadSite(siteId)
  }

  if (pageId) {
    siteStore.setCurrentPage(pageId)
  }

  // Load HTML content
  const content = siteStore.currentPage?.htmlContent || ''
  htmlCode.value = content
  originalHtml.value = content
  previewHtml.value = content

  document.addEventListener('keydown', onKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeyDown)
  if (previewTimeout) clearTimeout(previewTimeout)
})

// Watch for page changes (navigating between pages)
watch(() => siteStore.currentPage, (page) => {
  if (page?.htmlContent !== undefined) {
    htmlCode.value = page.htmlContent || ''
    originalHtml.value = page.htmlContent || ''
    previewHtml.value = page.htmlContent || ''
    isDirty.value = false
  }
})
</script>

<style scoped>
.html-editor-toolbar {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  background: #1e1e1e;
  color: white;
  border-bottom: 1px solid #333;
  position: sticky;
  top: 0;
  z-index: 100;
  height: 48px;
}

.html-editor-body {
  display: flex;
  height: calc(100vh - 48px);
  overflow: hidden;
}

.html-editor-body.layout-split .code-panel,
.html-editor-body.layout-split .preview-panel {
  width: 50%;
}

.html-editor-body.layout-code .code-panel {
  width: 100%;
}

.html-editor-body.layout-preview .preview-panel {
  width: 100%;
}

.code-panel {
  display: flex;
  flex-direction: column;
  border-right: 1px solid #333;
  background: #1e1e1e;
}

.code-panel-header,
.preview-panel-header {
  display: flex;
  align-items: center;
  padding: 4px 12px;
  background: #252525;
  color: #ccc;
  border-bottom: 1px solid #333;
  height: 32px;
  flex-shrink: 0;
}

.code-textarea {
  flex: 1;
  width: 100%;
  resize: none;
  border: none;
  outline: none;
  padding: 16px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #d4d4d4;
  background: #1e1e1e;
  tab-size: 2;
  white-space: pre;
  overflow: auto;
}

.code-textarea:focus {
  outline: none;
}

.preview-panel {
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  overflow: hidden;
}

.preview-panel-header {
  background: #fafafa;
  color: #666;
  border-bottom: 1px solid #e0e0e0;
}

.preview-container {
  flex: 1;
  background: white;
  overflow: hidden;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}
</style>
