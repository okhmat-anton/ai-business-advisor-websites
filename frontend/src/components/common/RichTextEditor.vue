<template>
  <div class="rich-editor">
    <!-- Toolbar -->
    <div class="rich-editor__toolbar">
      <!-- Text format -->
      <v-btn-group density="compact" variant="text" class="toolbar-group">
        <v-btn
          icon size="x-small"
          :class="{ active: active.bold }"
          @mousedown.prevent="exec('bold')"
          title="Bold"
        >
          <v-icon size="16">mdi-format-bold</v-icon>
        </v-btn>
        <v-btn
          icon size="x-small"
          :class="{ active: active.italic }"
          @mousedown.prevent="exec('italic')"
          title="Italic"
        >
          <v-icon size="16">mdi-format-italic</v-icon>
        </v-btn>
        <v-btn
          icon size="x-small"
          :class="{ active: active.underline }"
          @mousedown.prevent="exec('underline')"
          title="Underline"
        >
          <v-icon size="16">mdi-format-underline</v-icon>
        </v-btn>
        <v-btn
          icon size="x-small"
          :class="{ active: active.strikeThrough }"
          @mousedown.prevent="exec('strikeThrough')"
          title="Strikethrough"
        >
          <v-icon size="16">mdi-format-strikethrough</v-icon>
        </v-btn>
      </v-btn-group>

      <div class="toolbar-divider" />

      <!-- Headings -->
      <v-btn-group density="compact" variant="text" class="toolbar-group">
        <v-btn
          size="x-small"
          :class="{ active: active.h1 }"
          @mousedown.prevent="execBlock('H1')"
          title="Heading 1"
        >H1</v-btn>
        <v-btn
          size="x-small"
          :class="{ active: active.h2 }"
          @mousedown.prevent="execBlock('H2')"
          title="Heading 2"
        >H2</v-btn>
        <v-btn
          size="x-small"
          :class="{ active: active.h3 }"
          @mousedown.prevent="execBlock('H3')"
          title="Heading 3"
        >H3</v-btn>
        <v-btn
          size="x-small"
          :class="{ active: active.blockquote }"
          @mousedown.prevent="execBlock('BLOCKQUOTE')"
          title="Quote"
        >
          <v-icon size="16">mdi-format-quote-close</v-icon>
        </v-btn>
      </v-btn-group>

      <div class="toolbar-divider" />

      <!-- Lists -->
      <v-btn-group density="compact" variant="text" class="toolbar-group">
        <v-btn
          icon size="x-small"
          :class="{ active: active.insertUnorderedList }"
          @mousedown.prevent="exec('insertUnorderedList')"
          title="Bullet list"
        >
          <v-icon size="16">mdi-format-list-bulleted</v-icon>
        </v-btn>
        <v-btn
          icon size="x-small"
          :class="{ active: active.insertOrderedList }"
          @mousedown.prevent="exec('insertOrderedList')"
          title="Numbered list"
        >
          <v-icon size="16">mdi-format-list-numbered</v-icon>
        </v-btn>
      </v-btn-group>

      <div class="toolbar-divider" />

      <!-- Alignment -->
      <v-btn-group density="compact" variant="text" class="toolbar-group">
        <v-btn icon size="x-small" @mousedown.prevent="exec('justifyLeft')" title="Align left">
          <v-icon size="16">mdi-format-align-left</v-icon>
        </v-btn>
        <v-btn icon size="x-small" @mousedown.prevent="exec('justifyCenter')" title="Align center">
          <v-icon size="16">mdi-format-align-center</v-icon>
        </v-btn>
        <v-btn icon size="x-small" @mousedown.prevent="exec('justifyRight')" title="Align right">
          <v-icon size="16">mdi-format-align-right</v-icon>
        </v-btn>
      </v-btn-group>

      <div class="toolbar-divider" />

      <!-- Link -->
      <v-btn icon size="x-small" :class="{ active: active.link }" @mousedown.prevent="insertLink" title="Insert link">
        <v-icon size="16">mdi-link</v-icon>
      </v-btn>
      <v-btn icon size="x-small" @mousedown.prevent="exec('unlink')" title="Remove link">
        <v-icon size="16">mdi-link-off</v-icon>
      </v-btn>

      <div class="toolbar-divider" />

      <!-- Clear formatting -->
      <v-btn icon size="x-small" @mousedown.prevent="exec('removeFormat')" title="Clear formatting">
        <v-icon size="16">mdi-format-clear</v-icon>
      </v-btn>
    </div>

    <!-- Editable area -->
    <div
      ref="editorEl"
      class="rich-editor__content"
      contenteditable="true"
      :data-placeholder="placeholder"
      @input="onInput"
      @keyup="updateActive"
      @mouseup="updateActive"
      @focus="onFocus"
      @blur="onBlur"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, reactive } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: string
  placeholder?: string
}>(), {
  placeholder: 'Enter text…',
})

const emit = defineEmits<{
  (e: 'update:modelValue', val: string): void
}>()

const editorEl = ref<HTMLDivElement | null>(null)
// Track which formats are currently active in the selection
const active = reactive({
  bold: false,
  italic: false,
  underline: false,
  strikeThrough: false,
  insertUnorderedList: false,
  insertOrderedList: false,
  h1: false,
  h2: false,
  h3: false,
  blockquote: false,
  link: false,
})

// Sync modelValue → DOM (only when not focused to avoid cursor jump)
let isFocused = false
watch(() => props.modelValue, (val) => {
  if (!isFocused && editorEl.value && editorEl.value.innerHTML !== val) {
    editorEl.value.innerHTML = val || ''
  }
})
onMounted(() => {
  if (editorEl.value) editorEl.value.innerHTML = props.modelValue || ''
})

function onFocus() { isFocused = true }
function onBlur() {
  isFocused = false
  if (editorEl.value) emit('update:modelValue', editorEl.value.innerHTML)
}
function onInput() {
  if (editorEl.value) emit('update:modelValue', editorEl.value.innerHTML)
}

// Run execCommand (still the simplest cross-browser approach for contenteditable)
function exec(cmd: string, value?: string) {
  editorEl.value?.focus()
  document.execCommand(cmd, false, value)
  updateActive()
  if (editorEl.value) emit('update:modelValue', editorEl.value.innerHTML)
}

// Wrap / unwrap block-level tags (H1, H2, H3, BLOCKQUOTE)
function execBlock(tag: string) {
  editorEl.value?.focus()
  const sel = window.getSelection()
  if (!sel || !editorEl.value) return

  // Check if selection is already inside this tag — toggle off
  let node: Node | null = sel.anchorNode
  while (node && node !== editorEl.value) {
    if ((node as Element).tagName === tag) {
      // Replace the block with a P / DIV
      document.execCommand('formatBlock', false, 'p')
      updateActive()
      if (editorEl.value) emit('update:modelValue', editorEl.value.innerHTML)
      return
    }
    node = node.parentNode
  }
  document.execCommand('formatBlock', false, tag)
  updateActive()
  if (editorEl.value) emit('update:modelValue', editorEl.value.innerHTML)
}

function insertLink() {
  editorEl.value?.focus()
  const sel = window.getSelection()
  const existing = sel?.anchorNode ? findAnchorTag(sel.anchorNode) : null
  if (existing) {
    const url = prompt('Edit URL:', existing.href)
    if (url !== null) {
      existing.href = url || '#'
      if (editorEl.value) emit('update:modelValue', editorEl.value.innerHTML)
    }
    return
  }
  const url = prompt('Enter URL:')
  if (!url) return
  exec('createLink', url)
}

function findAnchorTag(node: Node): HTMLAnchorElement | null {
  let n: Node | null = node
  while (n) {
    if ((n as Element).tagName === 'A') return n as HTMLAnchorElement
    n = n.parentNode
  }
  return null
}

function updateActive() {
  active.bold = document.queryCommandState('bold')
  active.italic = document.queryCommandState('italic')
  active.underline = document.queryCommandState('underline')
  active.strikeThrough = document.queryCommandState('strikeThrough')
  active.insertUnorderedList = document.queryCommandState('insertUnorderedList')
  active.insertOrderedList = document.queryCommandState('insertOrderedList')

  const sel = window.getSelection()
  let node: Node | null = sel?.anchorNode ?? null
  active.h1 = false; active.h2 = false; active.h3 = false; active.blockquote = false; active.link = false
  while (node && node !== editorEl.value) {
    const tag = (node as Element).tagName
    if (tag === 'H1') active.h1 = true
    if (tag === 'H2') active.h2 = true
    if (tag === 'H3') active.h3 = true
    if (tag === 'BLOCKQUOTE') active.blockquote = true
    if (tag === 'A') active.link = true
    node = node.parentNode
  }
}
</script>

<style scoped>
.rich-editor {
  border: 1px solid rgba(0,0,0,0.23);
  border-radius: 4px;
  overflow: hidden;
  transition: border-color 0.2s;
}
.rich-editor:focus-within {
  border-color: rgb(var(--v-theme-primary));
  border-width: 2px;
}

/* Toolbar */
.rich-editor__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 2px;
  padding: 4px 6px;
  background: rgba(0,0,0,0.03);
  border-bottom: 1px solid rgba(0,0,0,0.10);
  min-height: 36px;
}
.toolbar-group {
  display: flex;
  align-items: center;
}
.toolbar-divider {
  width: 1px;
  height: 18px;
  background: rgba(0,0,0,0.15);
  margin: 0 3px;
  flex-shrink: 0;
}

/* Active state for toolbar buttons */
:deep(.active) {
  background: rgba(var(--v-theme-primary), 0.15) !important;
  color: rgb(var(--v-theme-primary)) !important;
}

/* Editable content area */
.rich-editor__content {
  min-height: 100px;
  padding: 10px 12px;
  outline: none;
  font-size: 14px;
  line-height: 1.6;
  color: inherit;
  overflow-y: auto;
}
.rich-editor__content:empty:before {
  content: attr(data-placeholder);
  color: rgba(0,0,0,0.38);
  pointer-events: none;
}

/* Styles inside the editor */
.rich-editor__content :deep(h1) { font-size: 1.5em; font-weight: 700; margin: 8px 0 4px; }
.rich-editor__content :deep(h2) { font-size: 1.25em; font-weight: 700; margin: 8px 0 4px; }
.rich-editor__content :deep(h3) { font-size: 1.1em; font-weight: 600; margin: 6px 0 4px; }
.rich-editor__content :deep(ul),
.rich-editor__content :deep(ol) { padding-left: 20px; margin: 4px 0; }
.rich-editor__content :deep(blockquote) {
  border-left: 3px solid rgba(var(--v-theme-primary), 0.7);
  padding-left: 10px;
  margin: 6px 0;
  color: rgba(0,0,0,0.6);
  font-style: italic;
}
.rich-editor__content :deep(a) { color: rgb(var(--v-theme-primary)); text-decoration: underline; }
.rich-editor__content :deep(p) { margin: 2px 0; }
</style>
