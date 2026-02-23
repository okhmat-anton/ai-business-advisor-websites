<template>
  <PublicLayout>
    <v-container fluid class="pa-6">
      <!-- Loading -->
      <div v-if="siteStore.isLoading" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="48" />
      </div>

      <template v-else-if="siteStore.currentSite">
        <!-- Header: breadcrumb + site name -->
        <div class="d-flex align-center mb-2">
          <v-btn icon variant="text" size="small" @click="goBack" class="mr-2">
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
          <v-breadcrumbs :items="breadcrumbs" density="compact" class="pa-0" />
        </div>

        <div class="d-flex align-center mb-6">
          <div>
            <h1 class="text-h4 font-weight-bold">{{ siteStore.currentSite.name }}</h1>
            <p class="text-body-2 text-grey">
              {{ siteStore.currentSite.description || 'Site pages' }}
              <v-chip
                v-if="isImported"
                size="x-small"
                color="warning"
                variant="tonal"
                class="ml-2"
              >
                Imported
              </v-chip>
              <v-chip
                :color="siteStore.currentSite.isPublished ? 'success' : 'grey'"
                size="x-small"
                variant="tonal"
                class="ml-2"
              >
                {{ siteStore.currentSite.isPublished ? 'Published' : 'Draft' }}
              </v-chip>
            </p>
          </div>
          <v-spacer />

          <!-- Publish button for imported sites -->
          <v-btn
            v-if="isImported"
            color="success"
            variant="flat"
            prepend-icon="mdi-publish"
            @click="publishSite"
          >
            Publish
          </v-btn>

          <!-- Normal site actions (hidden for imported) -->
          <template v-if="!isImported">
            <v-btn
              variant="outlined"
              prepend-icon="mdi-cog"
              class="mr-3"
              @click="showSettings = true"
            >
              Site Settings
            </v-btn>

            <v-btn
              color="primary"
              variant="flat"
              prepend-icon="mdi-plus"
              @click="showAddPage = true"
            >
              Add Page
            </v-btn>
          </template>
        </div>

        <!-- Empty state -->
        <v-card
          v-if="pages.length === 0"
          variant="outlined"
          class="pa-12 text-center"
        >
          <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-file-plus-outline</v-icon>
          <h3 class="text-h6 mb-2">No pages yet</h3>
          <p class="text-body-2 text-grey mb-4">
            Create your first page to start building this site
          </p>
          <v-btn color="primary" variant="flat" @click="showAddPage = true">
            Create Page
          </v-btn>
        </v-card>

        <!-- Pages table/list -->
        <v-card v-else variant="outlined" class="pages-card">
          <v-list lines="two" class="py-0">
            <template v-for="(page, index) in pages" :key="page.id">
              <v-list-item
                class="page-item"
                @click="isImported ? openPagePreview(page) : openPageEditor(page)"
              >
                <template #prepend>
                  <v-avatar color="primary" variant="tonal" size="40" class="mr-3">
                    <v-icon size="20">
                      {{ page.isHomePage ? 'mdi-home' : 'mdi-file-document-outline' }}
                    </v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title class="font-weight-medium">
                  {{ page.title }}
                  <v-chip
                    v-if="page.isHomePage"
                    size="x-small"
                    color="primary"
                    variant="tonal"
                    class="ml-2"
                  >
                    Home
                  </v-chip>
                  <v-chip
                    v-if="page.isMain"
                    size="x-small"
                    color="info"
                    variant="tonal"
                    class="ml-1"
                  >
                    Main
                  </v-chip>
                </v-list-item-title>

                <v-list-item-subtitle>
                  <span class="text-grey">/{{ page.slug || '' }}</span>
                  <span class="mx-2">&bull;</span>
                  <v-chip
                    :color="page.status === 'published' ? 'success' : 'grey'"
                    size="x-small"
                    variant="tonal"
                  >
                    {{ page.status === 'published' ? 'Published' : 'Draft' }}
                  </v-chip>
                  <span class="mx-2">&bull;</span>
                  <span class="text-grey text-caption">{{ formatDate(page.updatedAt) }}</span>
                </v-list-item-subtitle>

                <template #append>
                  <!-- Imported sites: preview only -->
                  <template v-if="isImported">
                    <v-btn
                      variant="tonal"
                      size="small"
                      color="primary"
                      prepend-icon="mdi-eye"
                      @click.stop="openPagePreview(page)"
                    >
                      Preview
                    </v-btn>
                  </template>

                  <!-- Normal sites: edit + menu -->
                  <template v-else>
                    <v-btn
                      icon
                      variant="text"
                      size="small"
                      color="primary"
                      class="mr-1"
                      @click.stop="openPageEditor(page)"
                    >
                      <v-icon size="20">mdi-pencil</v-icon>
                      <v-tooltip activator="parent" location="bottom">Edit Page</v-tooltip>
                    </v-btn>

                    <v-menu>
                      <template #activator="{ props }">
                        <v-btn icon variant="text" size="small" v-bind="props" @click.stop>
                          <v-icon>mdi-dots-vertical</v-icon>
                        </v-btn>
                      </template>
                      <v-list density="compact" min-width="160">
                        <v-list-item @click="openPageEditor(page)">
                          <template #prepend>
                            <v-icon size="18">mdi-pencil</v-icon>
                          </template>
                          <v-list-item-title>Edit</v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="editPageMeta(page)">
                          <template #prepend>
                            <v-icon size="18">mdi-cog</v-icon>
                          </template>
                          <v-list-item-title>Settings</v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="duplicatePage(page)">
                          <template #prepend>
                            <v-icon size="18">mdi-content-copy</v-icon>
                          </template>
                          <v-list-item-title>Duplicate</v-list-item-title>
                        </v-list-item>
                        <v-list-item
                          v-if="!page.isHomePage"
                          @click="toggleHomePage(page)"
                        >
                          <template #prepend>
                            <v-icon size="18">mdi-home</v-icon>
                          </template>
                          <v-list-item-title>Set as Home</v-list-item-title>
                        </v-list-item>
                        <v-divider />
                        <v-list-item
                          @click="confirmDeletePage(page)"
                          :disabled="page.isHomePage && pages.length > 1"
                        >
                          <template #prepend>
                            <v-icon size="18" color="error">mdi-delete</v-icon>
                          </template>
                          <v-list-item-title class="text-error">Delete</v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </template>
                </template>
              </v-list-item>
              <v-divider v-if="index < pages.length - 1" />
            </template>
          </v-list>
        </v-card>
      </template>

      <!-- Add page dialog -->
      <v-dialog v-model="showAddPage" max-width="440" persistent>
        <v-card>
          <v-card-title class="pa-4">Create New Page</v-card-title>
          <v-card-text class="pa-4 pt-0">
            <v-text-field
              v-model="newPageTitle"
              label="Page Title"
              variant="outlined"
              density="compact"
              autofocus
              hide-details="auto"
              class="mb-3"
              @keyup.enter="addPage"
            />
            <v-text-field
              v-model="newPageSlug"
              label="URL Slug"
              variant="outlined"
              density="compact"
              hide-details="auto"
              prefix="/"
              :placeholder="slugify(newPageTitle)"
            />
          </v-card-text>
          <v-card-actions class="pa-4 pt-0">
            <v-spacer />
            <v-btn variant="text" @click="closeAddPage">Cancel</v-btn>
            <v-btn
              color="primary"
              variant="flat"
              :disabled="!newPageTitle.trim()"
              @click="addPage"
            >
              Create
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Edit page meta dialog -->
      <v-dialog v-model="showEditPage" max-width="500" persistent>
        <v-card v-if="editingPage">
          <v-card-title class="pa-4">Page Settings</v-card-title>
          <v-card-text class="pa-4 pt-0">
            <v-text-field
              v-model="editingPage.title"
              label="Page Title"
              variant="outlined"
              density="compact"
              hide-details="auto"
              class="mb-3"
            />
            <v-text-field
              v-model="editingPage.slug"
              label="URL Slug"
              variant="outlined"
              density="compact"
              hide-details="auto"
              prefix="/"
              class="mb-3"
            />
            <v-text-field
              v-model="editingPage.seo.title"
              label="SEO Title"
              variant="outlined"
              density="compact"
              hide-details="auto"
              class="mb-3"
            />
            <v-textarea
              v-model="editingPage.seo.description"
              label="SEO Description"
              variant="outlined"
              density="compact"
              rows="2"
              hide-details="auto"
              class="mb-3"
            />
            <v-text-field
              v-model="editingPage.seo.keywords"
              label="SEO Keywords"
              variant="outlined"
              density="compact"
              hide-details="auto"
            />
          </v-card-text>
          <v-card-actions class="pa-4 pt-0">
            <v-spacer />
            <v-btn variant="text" @click="showEditPage = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" @click="savePageMeta">
              Save
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Delete confirm dialog -->
      <ConfirmDialog
        v-model="showDeleteConfirm"
        title="Delete Page"
        :message="`Are you sure you want to delete '${deletingPage?.title}'? This action cannot be undone.`"
        confirm-text="Delete"
        confirm-color="error"
        @confirm="deletePage"
      />

      <!-- Site settings dialog (reuse existing) -->
      <v-dialog v-model="showSettings" max-width="600" persistent>
        <v-card>
          <v-card-title class="d-flex align-center pa-4">
            <span>Site Settings</span>
            <v-spacer />
            <v-btn icon variant="text" size="small" @click="showSettings = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text class="pa-4 pt-0">
            <v-text-field
              v-model="siteNameEdit"
              label="Site Name"
              variant="outlined"
              density="compact"
              hide-details="auto"
              class="mb-3"
            />
            <v-textarea
              v-model="siteDescEdit"
              label="Description"
              variant="outlined"
              density="compact"
              rows="2"
              hide-details="auto"
              class="mb-3"
            />
            <v-text-field
              v-model="siteSubdomainEdit"
              label="Subdomain"
              variant="outlined"
              density="compact"
              hide-details="auto"
              suffix=".akm-advisor.com"
            />
          </v-card-text>
          <v-card-actions class="pa-4 pt-0">
            <v-spacer />
            <v-btn variant="text" @click="showSettings = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" @click="saveSiteSettings">
              Save
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </PublicLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSiteStore } from '@/stores/siteStore'
import type { IPage } from '@/types/site'
import { slugify } from '@/utils/helpers'
import PublicLayout from '@/layouts/PublicLayout.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const route = useRoute()
const router = useRouter()
const siteStore = useSiteStore()

// Pages list
const pages = computed(() => siteStore.currentSite?.pages || [])

// Is imported site (read-only)
const isImported = computed(() => siteStore.currentSite?.isImported === true)

// Add page
const showAddPage = ref(false)
const newPageTitle = ref('')
const newPageSlug = ref('')

// Edit page meta
const showEditPage = ref(false)
const editingPage = ref<IPage | null>(null)

// Delete
const showDeleteConfirm = ref(false)
const deletingPage = ref<IPage | null>(null)

// Site settings
const showSettings = ref(false)
const siteNameEdit = ref('')
const siteDescEdit = ref('')
const siteSubdomainEdit = ref('')

// Breadcrumbs
const breadcrumbs = computed(() => [
  { title: 'My Sites', to: '/' },
  { title: siteStore.currentSite?.name || 'Site', disabled: true },
])

onMounted(async () => {
  const siteId = route.params.siteId as string
  if (siteId) {
    await siteStore.loadSite(siteId)
  }
})

// Populate site settings fields when site loads
watch(() => siteStore.currentSite, (site) => {
  if (site) {
    siteNameEdit.value = site.name
    siteDescEdit.value = site.description || ''
    siteSubdomainEdit.value = site.subdomain || ''
  }
}, { immediate: true })

function goBack() {
  router.push('/')
}

function openPageEditor(page: IPage) {
  if (!siteStore.currentSite) return
  router.push(`/editor/${siteStore.currentSite.id}/${page.id}`)
}

function openPagePreview(page: IPage) {
  if (!siteStore.currentSite) return
  router.push(`/preview/${siteStore.currentSite.id}/${page.id}`)
}

async function publishSite() {
  if (!siteStore.currentSite) return
  await siteStore.publish()
}

// ===== Add Page =====
function closeAddPage() {
  showAddPage.value = false
  newPageTitle.value = ''
  newPageSlug.value = ''
}

async function addPage() {
  if (!siteStore.currentSite || !newPageTitle.value.trim()) return
  const slug = newPageSlug.value.trim() || slugify(newPageTitle.value)
  await siteStore.addPage(siteStore.currentSite.id, newPageTitle.value.trim())
  closeAddPage()
}

// ===== Edit Page Meta =====
function editPageMeta(page: IPage) {
  editingPage.value = JSON.parse(JSON.stringify(page))
  showEditPage.value = true
}

async function savePageMeta() {
  if (!siteStore.currentSite || !editingPage.value) return
  await siteStore.savePage(siteStore.currentSite.id, editingPage.value)
  showEditPage.value = false
  editingPage.value = null
}

// ===== Duplicate =====
async function duplicatePage(page: IPage) {
  if (!siteStore.currentSite) return
  await siteStore.addPage(siteStore.currentSite.id, `${page.title} (copy)`)
}

// ===== Set as Home =====
async function toggleHomePage(page: IPage) {
  if (!siteStore.currentSite) return
  // Unset previous home page
  for (const p of pages.value) {
    if (p.isHomePage && p.id !== page.id) {
      await siteStore.savePage(siteStore.currentSite.id, { ...p, isHomePage: false })
    }
  }
  await siteStore.savePage(siteStore.currentSite.id, { ...page, isHomePage: true })
}

// ===== Delete =====
function confirmDeletePage(page: IPage) {
  deletingPage.value = page
  showDeleteConfirm.value = true
}

async function deletePage() {
  if (!siteStore.currentSite || !deletingPage.value) return
  await siteStore.removePage(siteStore.currentSite.id, deletingPage.value.id)
  deletingPage.value = null
}

// ===== Site Settings =====
async function saveSiteSettings() {
  await siteStore.saveSite({
    name: siteNameEdit.value,
    description: siteDescEdit.value,
    subdomain: siteSubdomainEdit.value,
  })
  showSettings.value = false
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.pages-card {
  border-radius: 12px;
  overflow: hidden;
}

.page-item {
  cursor: pointer;
  transition: background-color 0.15s;
}

.page-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.04);
}
</style>
