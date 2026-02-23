<template>
  <div class="image-uploader">
    <v-text-field
      :model-value="modelValue"
      @update:model-value="$emit('update:modelValue', $event)"
      :label="label || 'Image URL'"
      density="compact"
      variant="outlined"
      hide-details
      prepend-inner-icon="mdi-image"
      :placeholder="placeholder || 'https://...'"
    />

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

    <!-- Sample images for mock -->
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
defineProps<{
  modelValue: string
  label?: string
  placeholder?: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()

const sampleImages = [
  'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800',
  'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800',
  'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800',
  'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800',
]
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
</style>
