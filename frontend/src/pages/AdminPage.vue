<template>
  <PublicLayout>
    <v-container fluid class="pa-6" style="max-width: 900px">
      <!-- Header -->
      <div class="d-flex align-center mb-6">
        <v-btn icon variant="text" size="small" class="mr-2" @click="$router.push('/')">
          <v-icon>mdi-arrow-left</v-icon>
        </v-btn>
        <div>
          <h1 class="text-h5 font-weight-bold">Admin Settings</h1>
          <p class="text-body-2 text-grey">Global configuration for the site builder</p>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="48" />
      </div>

      <template v-else>
        <!-- S3 Storage card -->
        <v-card variant="outlined" class="mb-6">
          <v-card-title class="d-flex align-center pa-4 pb-2">
            <v-icon class="mr-2" color="primary">mdi-cloud-upload</v-icon>
            S3 File Storage
            <v-spacer />
            <v-chip
              :color="form.s3.enabled ? 'success' : 'default'"
              size="small"
              variant="tonal"
            >
              {{ form.s3.enabled ? 'Active' : 'Disabled' }}
            </v-chip>
          </v-card-title>

          <v-card-text>
            <v-alert
              v-if="!form.s3.enabled"
              type="info"
              variant="tonal"
              density="compact"
              class="mb-4"
            >
              Files are stored on local disk. Enable S3 to upload images to cloud storage.
            </v-alert>
            <v-alert
              v-else
              type="success"
              variant="tonal"
              density="compact"
              class="mb-4"
            >
              Images will be uploaded to S3 bucket <strong>{{ form.s3.bucket || '(not set)' }}</strong>.
            </v-alert>

            <!-- Enable toggle -->
            <v-switch
              v-model="form.s3.enabled"
              label="Enable S3 storage"
              color="primary"
              density="compact"
              hide-details
              class="mb-4"
            />

            <v-row :class="{ 'opacity-50': !form.s3.enabled }">
              <!-- Bucket -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.s3.bucket"
                  label="Bucket name"
                  placeholder="my-bucket"
                  variant="outlined"
                  density="compact"
                  :disabled="!form.s3.enabled"
                  prepend-inner-icon="mdi-bucket"
                  hide-details="auto"
                />
              </v-col>

              <!-- Region -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.s3.region"
                  label="Region"
                  placeholder="us-east-1"
                  variant="outlined"
                  density="compact"
                  :disabled="!form.s3.enabled"
                  prepend-inner-icon="mdi-map-marker"
                  hide-details="auto"
                />
              </v-col>

              <!-- Access Key -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.s3.accessKey"
                  label="Access Key ID"
                  placeholder="AKIAIOSFODNN7EXAMPLE"
                  variant="outlined"
                  density="compact"
                  :disabled="!form.s3.enabled"
                  prepend-inner-icon="mdi-key"
                  hide-details="auto"
                />
              </v-col>

              <!-- Secret Key -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.s3.secretKey"
                  label="Secret Access Key"
                  :type="showSecret ? 'text' : 'password'"
                  placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                  variant="outlined"
                  density="compact"
                  :disabled="!form.s3.enabled"
                  prepend-inner-icon="mdi-lock"
                  :append-inner-icon="showSecret ? 'mdi-eye-off' : 'mdi-eye'"
                  @click:append-inner="showSecret = !showSecret"
                  hide-details="auto"
                />
              </v-col>

              <!-- Folder -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.s3.folder"
                  label="Upload folder (prefix)"
                  placeholder="uploads"
                  variant="outlined"
                  density="compact"
                  :disabled="!form.s3.enabled"
                  prepend-inner-icon="mdi-folder"
                  hide-details="auto"
                />
              </v-col>

              <v-col cols="12">
                <v-divider class="my-2" />
                <p class="text-caption text-grey mb-3">
                  Optional — leave empty for standard AWS S3. Fill in for S3-compatible storage
                  (DigitalOcean Spaces, MinIO, Cloudflare R2, etc.)
                </p>
              </v-col>

              <!-- Endpoint URL -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.s3.endpointUrl"
                  label="Custom Endpoint URL"
                  placeholder="https://nyc3.digitaloceanspaces.com"
                  variant="outlined"
                  density="compact"
                  :disabled="!form.s3.enabled"
                  prepend-inner-icon="mdi-web"
                  hint="Leave empty for real AWS S3"
                  persistent-hint
                />
              </v-col>

              <!-- Public URL -->
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.s3.publicUrl"
                  label="Public Base URL (CDN)"
                  placeholder="https://cdn.example.com"
                  variant="outlined"
                  density="compact"
                  :disabled="!form.s3.enabled"
                  prepend-inner-icon="mdi-link"
                  hint="Leave empty to auto-build from bucket + region"
                  persistent-hint
                />
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions class="pa-4 pt-0">
            <v-btn
              color="primary"
              variant="flat"
              :loading="saving"
              @click="save"
              prepend-icon="mdi-content-save"
            >
              Save Settings
            </v-btn>
            <v-btn
              variant="outlined"
              :loading="testing"
              :disabled="!form.s3.enabled || !form.s3.bucket"
              @click="testConnection"
              prepend-icon="mdi-connection"
              class="ml-2"
            >
              Test Connection
            </v-btn>
            <v-spacer />
            <v-chip
              v-if="testResult"
              :color="testResult.ok ? 'success' : 'error'"
              size="small"
              variant="tonal"
            >
              <v-icon start>{{ testResult.ok ? 'mdi-check-circle' : 'mdi-alert-circle' }}</v-icon>
              {{ testResult.message }}
            </v-chip>
          </v-card-actions>
        </v-card>
      </template>

      <!-- Snackbar -->
      <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000" location="bottom right">
        {{ snackbar.text }}
      </v-snackbar>
    </v-container>
  </PublicLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import PublicLayout from '@/layouts/PublicLayout.vue'
import { getAdminSettings, updateAdminSettings } from '@/api/api'
import type { IAdminSettings } from '@/api/api'
import apiClient from '@/api/index'

// ── State ─────────────────────────────────────────────────────────────────────
const loading = ref(true)
const saving = ref(false)
const testing = ref(false)
const showSecret = ref(false)
const testResult = ref<{ ok: boolean; message: string } | null>(null)

const snackbar = ref({ show: false, text: '', color: 'success' })

const form = ref<IAdminSettings>({
  s3: {
    enabled: false,
    bucket: '',
    region: 'us-east-1',
    accessKey: '',
    secretKey: '',
    endpointUrl: '',
    publicUrl: '',
    folder: 'uploads',
  },
})

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const data = await getAdminSettings()
    form.value = data
  } catch (err) {
    showSnackbar('Failed to load settings', 'error')
  } finally {
    loading.value = false
  }
})

// ── Actions ───────────────────────────────────────────────────────────────────
async function save() {
  saving.value = true
  testResult.value = null
  try {
    const updated = await updateAdminSettings({ s3: form.value.s3 })
    form.value = updated
    showSnackbar('Settings saved', 'success')
  } catch (err) {
    showSnackbar('Failed to save settings', 'error')
  } finally {
    saving.value = false
  }
}

async function testConnection() {
  testing.value = true
  testResult.value = null
  try {
    // Save first so backend uses latest credentials
    await updateAdminSettings({ s3: form.value.s3 })
    const { data } = await apiClient.post('/admin/test-s3')
    testResult.value = { ok: true, message: data.message || 'Connection successful' }
  } catch (err: any) {
    const msg = err?.response?.data?.detail || err?.message || 'Connection failed'
    testResult.value = { ok: false, message: msg }
  } finally {
    testing.value = false
  }
}

function showSnackbar(text: string, color = 'success') {
  snackbar.value = { show: true, text, color }
}
</script>

<style scoped>
.opacity-50 {
  opacity: 0.5;
  pointer-events: none;
}
</style>
