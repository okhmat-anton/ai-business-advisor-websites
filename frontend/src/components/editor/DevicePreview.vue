<template>
  <div class="device-preview-switcher d-flex align-center">
    <v-btn-toggle
      v-model="deviceMode"
      density="compact"
      variant="outlined"
      divided
      mandatory
      color="primary"
    >
      <v-btn value="desktop" size="small">
        <v-icon size="18">mdi-monitor</v-icon>
        <v-tooltip activator="parent" location="bottom">Desktop (1200px)</v-tooltip>
      </v-btn>
      <v-btn value="tablet_v" size="small">
        <v-icon size="18">mdi-tablet</v-icon>
        <v-tooltip activator="parent" location="bottom">Tablet (768px)</v-tooltip>
      </v-btn>
      <v-btn value="phone_v" size="small">
        <v-icon size="18">mdi-cellphone</v-icon>
        <v-tooltip activator="parent" location="bottom">Mobile (375px)</v-tooltip>
      </v-btn>
    </v-btn-toggle>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUiStore } from '@/stores/uiStore'

const uiStore = useUiStore()

const deviceMode = computed({
  get: () => uiStore.devicePreview,
  set: (val: string) => uiStore.setDevicePreview(val as any),
})
</script>

<style scoped>
.device-preview-switcher {
  user-select: none;
}
</style>
