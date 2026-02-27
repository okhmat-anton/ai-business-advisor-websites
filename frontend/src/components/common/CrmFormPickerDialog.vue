<template>
  <v-dialog v-model="show" max-width="560" scrollable>
    <v-card>
      <v-card-title class="d-flex align-center pa-4">
        <v-icon class="mr-2" color="primary">mdi-form-select</v-icon>
        Insert CRM Form
        <v-spacer />
        <v-btn icon variant="text" size="small" @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <!-- Mode tabs -->
      <v-tabs v-model="mode" density="compact" class="px-2">
        <v-tab value="list" prepend-icon="mdi-format-list-bulleted">CRM Forms</v-tab>
        <v-tab value="manual" prepend-icon="mdi-code-tags">Paste Code</v-tab>
      </v-tabs>

      <v-divider />

      <v-card-text class="pa-0" style="min-height: 260px">
        <!-- ─── CRM Forms list mode ─── -->
        <template v-if="mode === 'list'">
          <!-- Search + refresh -->
          <div class="pa-3 d-flex align-center gap-2">
            <v-text-field
              v-model="search"
              placeholder="Search forms..."
              density="compact"
              variant="outlined"
              hide-details
              prepend-inner-icon="mdi-magnify"
              clearable
              style="flex: 1"
            />
            <v-btn icon variant="tonal" size="small" @click="loadForms" :loading="loading">
              <v-icon size="18">mdi-refresh</v-icon>
            </v-btn>
          </div>

          <v-divider />

          <!-- Loading -->
          <div v-if="loading" class="d-flex justify-center align-center pa-8">
            <v-progress-circular indeterminate color="primary" />
          </div>

          <!-- Error with hint to use manual mode -->
          <div v-else-if="error" class="pa-3">
            <v-alert type="warning" variant="tonal" density="compact" class="mb-2">
              {{ error }}
            </v-alert>
            <p class="text-caption text-grey text-center">
              Try the <strong>"Paste Code"</strong> tab to insert embed code manually.
            </p>
          </div>

          <!-- Empty -->
          <div v-else-if="filteredForms.length === 0" class="pa-8 text-center text-grey">
            <v-icon size="48" class="mb-2">mdi-form-textbox</v-icon>
            <p>{{ search ? 'No forms match your search' : 'No forms found in CRM' }}</p>
          </div>

          <!-- Forms list -->
          <v-list v-else class="py-0" style="max-height: 320px; overflow-y: auto">
            <v-list-item
              v-for="form in filteredForms"
              :key="form.id"
              :active="selectedFormId === form.id"
              active-color="primary"
              class="cursor-pointer"
              @click="selectForm(form)"
            >
              <template #prepend>
                <v-avatar size="36" color="primary" variant="tonal">
                  <v-icon size="18">mdi-form-textbox</v-icon>
                </v-avatar>
              </template>

              <v-list-item-title class="font-weight-medium">{{ form.name }}</v-list-item-title>
              <v-list-item-subtitle>
                <span class="text-caption">/{{ form.slug }}</span>
                <span v-if="form.fields?.length" class="mx-1 text-caption text-grey">&bull;</span>
                <span v-if="form.fields?.length" class="text-caption text-grey">
                  {{ form.fields.length }} fields
                </span>
              </v-list-item-subtitle>

              <template #append>
                <v-icon v-if="selectedFormId === form.id" color="primary" size="20">
                  mdi-check-circle
                </v-icon>
                <v-chip
                  v-if="form.is_active === false"
                  size="x-small"
                  color="warning"
                  variant="tonal"
                >
                  Inactive
                </v-chip>
              </template>
            </v-list-item>
          </v-list>

          <!-- Embed code preview for selected form -->
          <template v-if="selectedForm && embedCode">
            <v-divider />
            <div class="pa-3 bg-grey-lighten-5">
              <div class="text-caption text-grey mb-1 d-flex align-center">
                <v-icon size="14" class="mr-1">mdi-code-tags</v-icon>
                Embed code preview
              </div>
              <pre class="embed-preview text-caption">{{ embedCode }}</pre>
            </div>
          </template>
        </template>

        <!-- ─── Manual paste mode ─── -->
        <template v-else>
          <div class="pa-4">
            <p class="text-body-2 text-grey mb-3">
              Paste the embed code from your form builder or CRM:
            </p>
            <v-textarea
              v-model="manualEmbedCode"
              label="Embed code"
              placeholder="<div data-form-id=...></div>&#10;<script src=...></script>"
              variant="outlined"
              rows="6"
              hide-details
              class="mb-3"
              style="font-family: 'Consolas', 'Monaco', monospace; font-size: 13px"
            />
            <v-text-field
              v-model="manualFormName"
              label="Form name (optional)"
              density="compact"
              variant="outlined"
              hide-details
              placeholder="e.g. Contact Us"
            />
          </div>
        </template>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" @click="close">Cancel</v-btn>
        <v-btn
          color="primary"
          variant="flat"
          :disabled="mode === 'list' ? (!embedCode || loadingEmbed) : !manualEmbedCode.trim()"
          :loading="loadingEmbed"
          prepend-icon="mdi-plus"
          @click="insert"
        >
          Insert Form
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { fetchCrmForms, fetchCrmFormEmbedCode, type CrmForm } from '@/api/crm'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{
  'update:modelValue': [val: boolean]
  insert: [code: string]
  select: [data: { formId: string; formName: string; formSlug: string; embedCode: string }]
}>()

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

// Mode: 'list' = CRM API forms, 'manual' = paste embed code
const mode = ref<'list' | 'manual'>('list')

const forms = ref<CrmForm[]>([])
const search = ref('')
const loading = ref(false)
const error = ref('')
const selectedFormId = ref<string | null>(null)
const selectedForm = ref<CrmForm | null>(null)
const embedCode = ref('')
const loadingEmbed = ref(false)

// Manual mode
const manualEmbedCode = ref('')
const manualFormName = ref('')

const filteredForms = computed(() => {
  if (!search.value.trim()) return forms.value
  const q = search.value.toLowerCase()
  return forms.value.filter(
    (f) => f.name.toLowerCase().includes(q) || f.slug.toLowerCase().includes(q)
  )
})

watch(show, (val) => {
  if (val) {
    loadForms()
    // Reset selection
    selectedFormId.value = null
    selectedForm.value = null
    embedCode.value = ''
    search.value = ''
    manualEmbedCode.value = ''
    manualFormName.value = ''
    mode.value = 'list'
  }
})

async function loadForms() {
  loading.value = true
  error.value = ''
  try {
    forms.value = await fetchCrmForms()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load forms from CRM'
  } finally {
    loading.value = false
  }
}

async function selectForm(form: CrmForm) {
  selectedFormId.value = form.id
  selectedForm.value = form
  embedCode.value = ''
  loadingEmbed.value = true
  try {
    const data = await fetchCrmFormEmbedCode(form.id)
    // The API can return different keys, pick the first available
    embedCode.value =
      data.embed_code ||
      data.html ||
      data.iframe_code ||
      data.script_tag ||
      `<div data-form-id="${form.id}"></div>\n<script src="https://app.akm-advisor.com/api/v1/forms/embed/${form.slug}.js"><\/script>`
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Failed to load embed code'
  } finally {
    loadingEmbed.value = false
  }
}

function insert() {
  if (mode.value === 'manual') {
    const code = manualEmbedCode.value.trim()
    if (!code) return
    emit('insert', code)
    emit('select', {
      formId: '',
      formName: manualFormName.value.trim() || 'Custom form',
      formSlug: '',
      embedCode: code,
    })
    close()
    return
  }

  if (!embedCode.value || !selectedForm.value) return
  emit('insert', embedCode.value)
  emit('select', {
    formId: selectedForm.value.id,
    formName: selectedForm.value.name,
    formSlug: selectedForm.value.slug,
    embedCode: embedCode.value,
  })
  close()
}

function close() {
  show.value = false
}
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.embed-preview {
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 80px;
  overflow: hidden;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 11px;
  color: #333;
}
</style>
