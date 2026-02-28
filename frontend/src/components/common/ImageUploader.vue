<template>
  <div class="image-uploader">
    <!-- URL input row with upload button -->
    <div class="d-flex align-center gap-2">
      <v-text-field
        :model-value="modelValue"
        @update:model-value="$emit('update:modelValue', $event)"
        :label="label || 'Image URL'"
        density="compact"
        variant="outlined"
        hide-details
        prepend-inner-icon="mdi-image"
        :placeholder="placeholder || 'https://...'"
        class="flex-grow-1"
      />
      <v-btn
        icon
        variant="tonal"
        size="small"
        color="primary"
        :loading="uploading"
        :disabled="uploading"
        title="Upload image from your device"
        @click="triggerFileInput"
      >
        <v-icon size="18">mdi-upload</v-icon>
      </v-btn>
    </div>

    <!-- Hidden file input -->
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      style="display: none"
      @change="onFileSelected"
    />

    <!-- Upload error -->
    <div v-if="uploadError" class="text-caption text-error mt-1">
      {{ uploadError }}
    </div>

    <!-- Preview -->
    <div v-if="modelValue" class="preview mt-2">
      <v-img
        :src="modelValue"
        max-height="120"
        cover
        class="rounded"
      >
        <template #error>
          <div class="d-flex align-center justify-center fill-height bg-grey-lighten-3">
            <v-icon color="grey">mdi-image-broken</v-icon>
          </div>
        </template>
      </v-img>
      <v-btn
        icon
        variant="text"
        size="x-small"
        class="clear-btn"
        @click="$emit('update:modelValue', '')"
      >
        <v-icon size="16">mdi-close</v-icon>
      </v-btn>
    </div>

    <!-- Sample images -->
    <div class="mt-2">
      <div class="text-caption text-grey mb-1">Sample Images</div>
      <div class="d-flex flex-wrap gap-1">
        <v-img
          v-for="(img, idx) in sampleImages"
          :key="idx"
          :src="img"
          width="40"
          height="40"
          cover
          class="rounded cursor-pointer sample-thumb"
          @click="$emit('update:modelValue', img)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { uploadFile } from '@/api/api'

const props = defineProps<{
  modelValue: string
  label?: string
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const uploadError = ref('')

const sampleImages = [
  'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800',
  'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800',
  'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800',
  'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800',
]

function triggerFileInput() {
  uploadError.value = ''
  fileInputRef.value?.click()
}

async function onFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  // Reset input so the same file can be selected again
  input.value = ''

  uploading.value = true
  uploadError.value = ''
  try {
    const { url } = await uploadFile(file)
    if (url) {
      emit('update:modelValue', url)
    } else {
      uploadError.value = 'Upload failed: no URL returned'
    }
  } catch (err: any) {
    uploadError.value = err?.message || 'Upload failed'
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.image-uploader {
  position: relative;
}

.preview {
  position: relative;
}

.clear-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(255, 255, 255, 0.8);
}

.sample-thumb {
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.sample-thumb:hover {
  opacity: 1;
}

.gap-1 {
  gap: 4px;
}

.gap-2 {
  gap: 8px;
}
</style>
