<template>
  <PublicLayout>
    <v-container fluid class="pa-6">
      <!-- Header -->
      <div class="d-flex align-center mb-6">
        <div>
          <h1 class="text-h4 font-weight-bold">My Sites</h1>
          <p class="text-body-2 text-grey">Manage your websites</p>
        </div>
        <v-spacer />
        <v-btn
          variant="outlined"
          prepend-icon="mdi-folder-zip-outline"
          class="mr-3"
          @click="showZipImport = true"
        >
          Import ZIP
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          prepend-icon="mdi-plus"
          @click="createSite"
        >
          Create New Site
        </v-btn>
      </div>

      <!-- Loading -->
      <div v-if="siteStore.isLoading" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="48" />
      </div>

      <!-- Empty state -->
      <v-card
        v-else-if="siteStore.sites.length === 0"
        variant="outlined"
        class="pa-12 text-center"
      >
        <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-web-plus</v-icon>
        <h3 class="text-h6 mb-2">No websites yet</h3>
        <p class="text-body-2 text-grey mb-4">
          Create your first website to get started
        </p>
        <v-btn color="primary" variant="flat" @click="createSite">
          Create Website
        </v-btn>
      </v-card>

      <!-- Site grid -->
      <v-row v-else>
        <v-col
          v-for="site in siteStore.sites"
          :key="site.id"
          cols="12"
          sm="6"
          md="4"
          lg="3"
        >
          <v-card class="site-card" hover @click="openSite(site.id)">
            <!-- Site thumbnail -->
            <div class="site-thumbnail">
              <v-icon size="48" color="grey-lighten-1">mdi-web</v-icon>
            </div>

            <v-card-text class="pb-2">
              <h3 class="text-subtitle-1 font-weight-medium text-truncate">
                {{ site.name }}
              </h3>
              <p class="text-caption text-grey">
                {{ site.pages?.length || 0 }} pages
                <span class="mx-1">&bull;</span>
                {{ formatDate(site.updatedAt) }}
              </p>
            </v-card-text>

            <v-card-actions class="pt-0">
              <v-chip
                v-if="site.isImported"
                size="x-small"
                color="warning"
                variant="tonal"
              >
                Imported
              </v-chip>
              <v-chip
                :color="site.isPublished ? 'success' : 'grey'"
                size="x-small"
                variant="tonal"
              >
                {{ site.isPublished ? 'Published' : 'Draft' }}
              </v-chip>

              <v-spacer />

              <v-menu>
                <template #activator="{ props }">
                  <v-btn icon variant="text" size="small" v-bind="props" @click.stop>
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list density="compact">
                  <v-list-item @click="openSite(site.id)">
                    <template #prepend>
                      <v-icon size="18">mdi-pencil</v-icon>
                    </template>
                    <v-list-item-title>Edit</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="duplicateSite(site)">
                    <template #prepend>
                      <v-icon size="18">mdi-content-copy</v-icon>
                    </template>
                    <v-list-item-title>Duplicate</v-list-item-title>
                  </v-list-item>
                  <v-divider />
                  <v-list-item @click="confirmDelete(site)">
                    <template #prepend>
                      <v-icon size="18" color="error">mdi-delete</v-icon>
                    </template>
                    <v-list-item-title class="text-error">Delete</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <!-- ZIP Import dialog -->
      <ZipImportDialog v-model="showZipImport" />

      <!-- Delete confirm dialog -->
      <ConfirmDialog
        v-model="showDeleteConfirm"
        title="Delete Website"
        :message="`Are you sure you want to delete '${deletingSite?.name}'? This action cannot be undone.`"
        confirm-text="Delete"
        confirm-color="error"
        @confirm="deleteSite"
      />
    </v-container>
  </PublicLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSiteStore } from '@/stores/siteStore'
import type { ISite } from '@/types/site'
import PublicLayout from '@/layouts/PublicLayout.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import ZipImportDialog from '@/components/site/ZipImportDialog.vue'

const router = useRouter()
const siteStore = useSiteStore()

const showDeleteConfirm = ref(false)
const showZipImport = ref(false)
const deletingSite = ref<ISite | null>(null)

onMounted(async () => {
  await siteStore.loadSites()
})

function openSite(siteId: string) {
  router.push(`/sites/${siteId}`)
}

async function createSite() {
  const site = await siteStore.addSite('New Website')
  if (site) {
    router.push(`/sites/${site.id}`)
  }
}

async function duplicateSite(site: ISite) {
  await siteStore.addSite(`${site.name} (copy)`)
}

function confirmDelete(site: ISite) {
  deletingSite.value = site
  showDeleteConfirm.value = true
}

async function deleteSite() {
  if (deletingSite.value) {
    await siteStore.removeSite(deletingSite.value.id)
    deletingSite.value = null
  }
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>

<style scoped>
.site-card {
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
}

.site-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.site-thumbnail {
  height: 160px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
