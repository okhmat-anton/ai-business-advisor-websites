<template>
  <v-dialog v-model="show" max-width="500">
    <v-card>
      <v-card-title class="d-flex align-center pa-4">
        <span class="text-h6">Domain Settings</span>
        <v-spacer />
        <v-btn icon variant="text" @click="show = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-4">
        <!-- Tilda subdomain -->
        <div class="text-subtitle-2 mb-2">Default Domain</div>
        <v-text-field
          :model-value="defaultDomain"
          label="Subdomain"
          variant="outlined"
          density="compact"
          readonly
          class="mb-4"
          prepend-inner-icon="mdi-web"
        />

        <div class="text-subtitle-2 mb-2">Custom Domains</div>

        <div v-for="(domain, idx) in domains" :key="idx" class="d-flex align-center mb-2">
          <v-text-field
            :model-value="domain.domain"
            @update:model-value="(val: string) => { domain.domain = val }"
            label="Domain"
            variant="outlined"
            density="compact"
            hide-details
            prepend-inner-icon="mdi-earth"
          />
          <v-chip
            :color="domain.isVerified ? 'success' : 'warning'"
            size="small"
            class="mx-2"
          >
            {{ domain.isVerified ? 'Verified' : 'Pending' }}
          </v-chip>
          <v-btn icon variant="text" size="small" @click="removeDomain(idx)">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </div>

        <v-btn variant="tonal" color="primary" size="small" @click="addDomain" class="mt-2">
          <v-icon left>mdi-plus</v-icon>
          Add Domain
        </v-btn>

        <v-alert type="info" variant="tonal" density="compact" class="mt-4">
          <div class="text-caption">
            Point your domain's CNAME record to <strong>sites.akm-advisor.com</strong>
            to verify and connect your custom domain.
          </div>
        </v-alert>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" @click="show = false">Cancel</v-btn>
        <v-btn color="primary" variant="flat" @click="save">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive } from 'vue'
import { useSiteStore } from '@/stores/siteStore'

interface DomainEntry {
  domain: string
  isVerified: boolean
  isPrimary: boolean
}

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const siteStore = useSiteStore()

const show = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
})

const domains = ref<DomainEntry[]>([])

const defaultDomain = computed(() => {
  if (!siteStore.currentSite) return ''
  return `${siteStore.currentSite.subdomain || siteStore.currentSite.id}.akm-advisor.com`
})

watch(show, (val) => {
  if (val && siteStore.currentSite) {
    domains.value = (siteStore.currentSite.domains || []).map((d: any) => ({
      domain: d.domain || '',
      isVerified: d.isVerified || false,
      isPrimary: d.isPrimary || false,
    }))
  }
})

function addDomain() {
  domains.value.push({ domain: '', isVerified: false, isPrimary: false })
}

function removeDomain(idx: number) {
  domains.value.splice(idx, 1)
}

async function save() {
  // Mock save - in real app would call API
  show.value = false
}
</script>
