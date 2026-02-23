<template>
  <v-dialog v-model="show" max-width="600" persistent>
    <v-card class="zip-import-dialog">
      <!-- Header -->
      <v-card-title class="d-flex align-center pa-4">
        <v-icon class="mr-2" color="primary">mdi-folder-zip-outline</v-icon>
        <span class="text-h6">Import Website from ZIP</span>
        <v-spacer />
        <v-btn icon variant="text" size="small" @click="close" :disabled="importing">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-4">
        <!-- Step 1: Upload -->
        <div v-if="step === 'upload'">
          <div
            class="upload-zone"
            :class="{ 'upload-zone--drag': isDragging }"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="onDrop"
            @click="openFilePicker"
          >
            <v-icon size="48" color="grey-lighten-1" class="mb-3">mdi-cloud-upload-outline</v-icon>
            <p class="text-body-1 font-weight-medium mb-1">Drop ZIP file here</p>
            <p class="text-body-2 text-medium-emphasis">or click to browse</p>
            <p class="text-caption text-grey mt-2">Supports .zip files up to 100 MB</p>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept=".zip,application/zip,application/x-zip-compressed"
            style="display: none"
            @change="onFileSelect"
          />
        </div>

        <!-- Step 2: Preview — pick index page -->
        <div v-else-if="step === 'preview'">
          <v-alert type="info" variant="tonal" density="compact" class="mb-4">
            ZIP parsed successfully. Choose the main page (index.html).
          </v-alert>

          <!-- Site name -->
          <v-text-field
            v-model="siteName"
            label="Site Name"
            density="compact"
            variant="outlined"
            hide-details
            class="mb-4"
          />

          <!-- Pages found — user selects which is index -->
          <div class="text-subtitle-2 mb-2">
            Pages found: {{ importResult?.pages.length || 0 }}
          </div>
          <v-list density="compact" class="mb-3 border rounded" mandatory>
            <v-list-item
              v-for="page in importResult?.pages"
              :key="page.fileName"
              :title="page.title"
              :subtitle="page.fileName"
              :value="page.fileName"
              :active="selectedMainPage === page.fileName"
              @click="selectedMainPage = page.fileName"
              color="primary"
            >
              <template #prepend>
                <v-icon size="20" :color="selectedMainPage === page.fileName ? 'primary' : 'grey'">
                  {{ selectedMainPage === page.fileName ? 'mdi-radiobox-marked' : 'mdi-radiobox-blank' }}
                </v-icon>
              </template>
              <template #append>
                <v-chip
                  v-if="selectedMainPage === page.fileName"
                  size="x-small"
                  color="primary"
                  variant="tonal"
                >
                  index.html
                </v-chip>
              </template>
            </v-list-item>
          </v-list>
        </div>

        <!-- Step 3: Importing -->
        <div v-else-if="step === 'importing'" class="text-center py-6">
          <v-progress-circular indeterminate color="primary" size="48" class="mb-4" />
          <p class="text-body-1 font-weight-medium">Importing site...</p>
          <p class="text-body-2 text-medium-emphasis">{{ importStatus }}</p>
        </div>

        <!-- Step 4: Done -->
        <div v-else-if="step === 'done'" class="text-center py-6">
          <v-icon size="64" color="success" class="mb-3">mdi-check-circle-outline</v-icon>
          <p class="text-h6 mb-1">Import Complete!</p>
          <p class="text-body-2 text-medium-emphasis mb-4">
            {{ importResult?.pages.length }} page(s) imported successfully
          </p>
        </div>

        <!-- Error -->
        <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mt-3">
          {{ error }}
        </v-alert>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-btn v-if="step === 'preview'" variant="text" @click="reset">
          Back
        </v-btn>
        <v-spacer />
        <v-btn variant="text" @click="close" :disabled="importing">
          {{ step === 'done' ? 'Close' : 'Cancel' }}
        </v-btn>
        <v-btn
          v-if="step === 'preview'"
          color="primary"
          variant="flat"
          :loading="importing"
          @click="doImport"
        >
          Import Site
        </v-btn>
        <v-btn
          v-if="step === 'done'"
          color="primary"
          variant="flat"
          @click="openImportedSite"
        >
          Open Site
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSiteStore } from '@/stores/siteStore'
import {
  parseZipFile,
  isValidZipFile,
  formatFileSize,
  type ZipImportResult,
} from '@/utils/zipImport'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const router = useRouter()
const siteStore = useSiteStore()

type Step = 'upload' | 'preview' | 'importing' | 'done'

const step = ref<Step>('upload')
const isDragging = ref(false)
const importing = ref(false)
const error = ref('')
const importStatus = ref('')
const siteName = ref('')
const selectedMainPage = ref<string>('')
const importResult = ref<ZipImportResult | null>(null)
const importedSiteId = ref<string | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const show = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
})

function openFilePicker() {
  fileInput.value?.click()
}

function onFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) handleFile(file)
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) handleFile(file)
}

async function handleFile(file: File) {
  error.value = ''

  if (!isValidZipFile(file)) {
    error.value = 'Please select a valid .zip file'
    return
  }

  if (file.size > 100 * 1024 * 1024) {
    error.value = `File too large (${formatFileSize(file.size)}). Maximum size is 100 MB.`
    return
  }

  try {
    importResult.value = await parseZipFile(file)
    siteName.value = importResult.value.siteName

    if (importResult.value.pages.length === 0) {
      error.value = 'No HTML pages found in the ZIP archive'
      return
    }

    // Auto-select index.html or first page
    const mainPage = importResult.value.pages.find((p) => p.isMain)
    selectedMainPage.value = mainPage?.fileName || importResult.value.pages[0]?.fileName || ''

    step.value = 'preview'
  } catch (err: any) {
    error.value = `Failed to parse ZIP: ${err.message || 'Unknown error'}`
  }
}

async function doImport() {
  if (!importResult.value) return

  importing.value = true
  error.value = ''
  step.value = 'importing'

  try {
    // Create site (marked as imported)
    importStatus.value = 'Creating site...'
    const site = await siteStore.addSite(siteName.value || 'Imported Site', undefined, true)
    if (!site) throw new Error('Failed to create site')

    importedSiteId.value = site.id
    await siteStore.loadSite(site.id)

    // Save each page with raw HTML content
    for (let i = 0; i < importResult.value.pages.length; i++) {
      const pageData = importResult.value.pages[i]!
      const isMainPage = pageData.fileName === selectedMainPage.value
      importStatus.value = `Importing page ${i + 1}/${importResult.value.pages.length}: ${pageData.title}`

      if (i === 0 && siteStore.currentSite?.pages.length) {
        // Update the default page created with the site
        const defaultPage = siteStore.currentSite.pages[0]!
        await siteStore.savePage(site.id, {
          ...defaultPage,
          title: pageData.title,
          slug: pageData.slug,
          htmlContent: pageData.htmlContent,
          isMain: isMainPage,
          isHomePage: isMainPage,
        })
      } else {
        // Create new page and update it with HTML content
        const page = await siteStore.addPage(site.id, pageData.title)
        if (page) {
          await siteStore.savePage(site.id, {
            ...page,
            slug: pageData.slug,
            htmlContent: pageData.htmlContent,
            isMain: isMainPage,
            isHomePage: isMainPage,
          })
        }
      }
    }

    importStatus.value = 'Done!'
    step.value = 'done'
  } catch (err: any) {
    error.value = `Import failed: ${err.message || 'Unknown error'}`
    step.value = 'preview'
  } finally {
    importing.value = false
  }
}

function openImportedSite() {
  if (importedSiteId.value) {
    router.push(`/sites/${importedSiteId.value}`)
    close()
  }
}

function reset() {
  step.value = 'upload'
  importResult.value = null
  siteName.value = ''
  selectedMainPage.value = ''
  error.value = ''
}

function close() {
  show.value = false
  setTimeout(() => {
    step.value = 'upload'
    importResult.value = null
    siteName.value = ''
    selectedMainPage.value = ''
    error.value = ''
    importedSiteId.value = null
  }, 300)
}
</script>

<style scoped>
.upload-zone {
  border: 2px dashed rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(0, 0, 0, 0.02);
}

.upload-zone:hover {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.04);
}

.upload-zone--drag {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.08);
  transform: scale(1.01);
}

.border {
  border: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
