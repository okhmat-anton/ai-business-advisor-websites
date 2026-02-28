<template>
  <v-dialog v-model="show" max-width="600" persistent>
    <v-card>
      <v-card-title class="d-flex align-center pa-4">
        <span class="text-h6">Site Settings</span>
        <v-spacer />
        <v-btn icon variant="text" @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-4">
        <v-text-field
          v-model="form.name"
          label="Site Name"
          variant="outlined"
          density="compact"
          class="mb-3"
        />

        <v-text-field
          v-model="form.description"
          label="Site Description"
          variant="outlined"
          density="compact"
          class="mb-3"
        />

        <div class="text-subtitle-2 mb-2">Favicon</div>
        <div class="d-flex align-center gap-2 mb-1">
          <v-text-field
            v-model="form.favicon"
            label="Favicon URL (.ico, .png, .jpg)"
            variant="outlined"
            density="compact"
            hide-details
            prepend-inner-icon="mdi-star-four-points"
            class="flex-grow-1"
          />
          <v-btn
            icon
            variant="tonal"
            size="small"
            color="primary"
            :loading="faviconUploading"
            :disabled="faviconUploading"
            title="Upload favicon from device"
            @click="triggerFaviconInput"
          >
            <v-icon size="18">mdi-upload</v-icon>
          </v-btn>
        </div>
        <input
          ref="faviconInputRef"
          type="file"
          accept=".ico,.png,.jpg,.jpeg,.svg"
          style="display: none"
          @change="onFaviconSelected"
        />
        <div v-if="faviconError" class="text-caption text-error mb-2">{{ faviconError }}</div>
        <div v-if="form.favicon" class="d-flex align-center gap-2 mb-3">
          <img :src="form.favicon" width="32" height="32" style="object-fit: contain; border: 1px solid #e0e0e0; border-radius: 4px;" />
          <span class="text-caption text-grey">Preview (32×32)</span>
          <v-btn icon variant="text" size="x-small" @click="form.favicon = ''">
            <v-icon size="16">mdi-close</v-icon>
          </v-btn>
        </div>
        <div v-else class="mb-3" />

        <div class="text-subtitle-2 mb-2">Global Styles</div>

        <v-text-field
          v-model="form.globalSettings.primaryColor"
          label="Primary Color"
          variant="outlined"
          density="compact"
          prepend-inner-icon="mdi-palette"
          class="mb-3"
        >
          <template #append-inner>
            <div
              class="color-swatch"
              :style="{ background: form.globalSettings.primaryColor }"
            />
          </template>
        </v-text-field>

        <v-select
          v-model="form.globalSettings.fontFamily"
          :items="fontOptions"
          label="Font Family"
          variant="outlined"
          density="compact"
          class="mb-3"
        />

        <v-text-field
          v-model="form.globalSettings.customCss"
          label="Custom CSS (global)"
          variant="outlined"
          density="compact"
          prepend-inner-icon="mdi-code-braces"
          class="mb-3"
        />

        <v-textarea
          v-model="form.globalSettings.headScripts"
          label="Head Scripts"
          variant="outlined"
          density="compact"
          rows="3"
          placeholder="Custom scripts and meta tags..."
          class="mb-3"
        />
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" @click="close">Cancel</v-btn>
        <v-btn color="primary" variant="flat" @click="save">Save Settings</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useSiteStore } from '@/stores/siteStore'
import { useUiStore } from '@/stores/uiStore'
import { uploadFile } from '@/api/api'

const siteStore = useSiteStore()
const uiStore = useUiStore()

const fontOptions = [
  'Inter, sans-serif',
  'Roboto, sans-serif',
  'Open Sans, sans-serif',
  'Montserrat, sans-serif',
  'Lato, sans-serif',
  'Playfair Display, serif',
  'Georgia, serif',
  'monospace',
]

const form = reactive({
  name: '',
  description: '',
  favicon: '',
  globalSettings: {
    primaryColor: '#1976D2',
    fontFamily: 'Inter, sans-serif',
    customCss: '',
    headScripts: '',
  },
})

const show = computed({
  get: () => uiStore.showSiteSettings,
  set: (val: boolean) => {
    if (!val) uiStore.closeSiteSettings()
  },
})

// ── Favicon upload ────────────────────────────────────────────────────────────
const faviconInputRef = ref<HTMLInputElement | null>(null)
const faviconUploading = ref(false)
const faviconError = ref('')

function triggerFaviconInput() {
  faviconError.value = ''
  faviconInputRef.value?.click()
}

async function onFaviconSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  input.value = ''

  faviconUploading.value = true
  faviconError.value = ''
  try {
    const { url } = await uploadFile(file)
    if (url) {
      form.favicon = url
    } else {
      faviconError.value = 'Upload failed: no URL returned'
    }
  } catch (err: any) {
    faviconError.value = err?.message || 'Upload failed'
  } finally {
    faviconUploading.value = false
  }
}


watch(show, (val) => {
  if (val && siteStore.currentSite) {
    const site = siteStore.currentSite
    form.name = site.name
    form.description = site.description || ''
    form.favicon = site.favicon || ''
    form.globalSettings.primaryColor = site.globalSettings?.primaryColor || '#1976D2'
    form.globalSettings.fontFamily = site.globalSettings?.fontFamily || 'Inter, sans-serif'
    form.globalSettings.customCss = site.globalSettings?.customCss || ''
    form.globalSettings.headScripts = site.globalSettings?.headScripts || ''
  }
})

async function save() {
  if (!siteStore.currentSite) return
  await siteStore.saveSite({
    ...siteStore.currentSite,
    name: form.name,
    description: form.description,
    favicon: form.favicon,
    globalSettings: { ...form.globalSettings },
  })
  close()
}

function close() {
  uiStore.closeSiteSettings()
}
</script>

<style scoped>
.color-swatch {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}
</style>
