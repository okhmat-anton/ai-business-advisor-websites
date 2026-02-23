<template>
  <div class="color-picker-wrapper">
    <v-text-field
      :model-value="modelValue"
      @update:model-value="$emit('update:modelValue', $event)"
      :label="label"
      density="compact"
      variant="outlined"
      hide-details
    >
      <template #prepend-inner>
        <div
          class="color-dot"
          :style="{ backgroundColor: modelValue || '#ffffff' }"
          @click="showPicker = !showPicker"
        />
      </template>
    </v-text-field>

    <div v-if="showPicker" class="color-presets mt-2">
      <div
        v-for="color in presets"
        :key="color"
        class="preset"
        :class="{ active: modelValue === color }"
        :style="{ backgroundColor: color }"
        @click="selectColor(color)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  modelValue: string
  label?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const showPicker = ref(false)

const presets = [
  '#ffffff', '#f5f5f5', '#e0e0e0', '#9e9e9e', '#616161', '#212121',
  '#000000', '#f44336', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5',
  '#2196f3', '#03a9f4', '#00bcd4', '#009688', '#4caf50', '#8bc34a',
  '#cddc39', '#ffeb3b', '#ffc107', '#ff9800', '#ff5722', '#795548',
]

function selectColor(color: string) {
  emit('update:modelValue', color)
  showPicker.value = false
}
</script>

<style scoped>
.color-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid #ccc;
  cursor: pointer;
}

.color-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.preset {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform 0.15s;
}

.preset:hover {
  transform: scale(1.15);
}

.preset.active {
  border-color: #1976d2;
}
</style>
