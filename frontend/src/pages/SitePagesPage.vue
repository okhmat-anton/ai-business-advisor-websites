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

          <v-btn
            variant="outlined"
            prepend-icon="mdi-cog"
            class="mr-3"
            @click="showSettings = true"
          >
            Site Settings
          </v-btn>

          <v-btn
            color="success"
            variant="flat"
            prepend-icon="mdi-publish"
            class="mr-3"
            :loading="isPublishing"
            @click="publishSite"
          >
            Publish
          </v-btn>

          <v-btn
            v-if="!isImported"
            color="primary"
            variant="flat"
            prepend-icon="mdi-plus"
            @click="showAddPage = true"
          >
            Add Page
          </v-btn>
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
                @click="isImported ? openHtmlEditor(page) : openPageEditor(page)"
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

                <v-list-item-subtitle class="d-flex align-center flex-wrap">
                  <v-chip
                    size="x-small"
                    variant="tonal"
                    color="primary"
                    class="mr-1"
                    style="cursor:pointer"
                    prepend-icon="mdi-link"
                    @click.stop="editSlug(page)"
                  >
                    /{{ page.slug || '(no url)' }}
                    <v-icon end size="12">mdi-pencil</v-icon>
                  </v-chip>
                  <span class="mx-1">&bull;</span>
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
                  <!-- Imported sites: edit HTML + menu -->
                  <template v-if="isImported">
                    <v-btn
                      variant="tonal"
                      size="small"
                      color="primary"
                      prepend-icon="mdi-code-tags"
                      class="mr-1"
                      @click.stop="openHtmlEditor(page)"
                    >
                      Edit
                    </v-btn>
                    <v-btn
                      variant="tonal"
                      size="small"
                      color="grey"
                      prepend-icon="mdi-eye"
                      class="mr-1"
                      @click.stop="openPagePreview(page)"
                    >
                      Preview
                    </v-btn>

                    <v-menu>
                      <template #activator="{ props }">
                        <v-btn icon variant="text" size="small" v-bind="props" @click.stop>
                          <v-icon>mdi-dots-vertical</v-icon>
                        </v-btn>
                      </template>
                      <v-list density="compact" min-width="160">
                        <v-list-item @click="editPageMeta(page)">
                          <template #prepend>
                            <v-icon size="18">mdi-cog</v-icon>
                          </template>
                          <v-list-item-title>SEO / Settings</v-list-item-title>
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

      <!-- Site settings dialog with tabs -->
      <v-dialog v-model="showSettings" max-width="700" persistent>
        <v-card>
          <v-card-title class="d-flex align-center pa-4">
            <span>Site Settings</span>
            <v-spacer />
            <v-btn icon variant="text" size="small" @click="showSettings = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-title>

          <v-tabs v-model="settingsTab" color="primary">
            <v-tab value="general">General</v-tab>
            <v-tab value="domain">Domain</v-tab>
          </v-tabs>

          <v-divider />

          <v-tabs-window v-model="settingsTab">
            <!-- General tab -->
            <v-tabs-window-item value="general">
              <v-card-text class="pa-4">
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
                  class="mb-3"
                />

                <div class="text-subtitle-2 mb-2">Favicon</div>
                <div class="d-flex align-center gap-2 mb-1">
                  <v-text-field
                    v-model="siteFaviconEdit"
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
                <div v-if="faviconError" class="text-caption text-error mb-1">{{ faviconError }}</div>
                <div v-if="siteFaviconEdit" class="d-flex align-center gap-2 mt-1">
                  <img :src="siteFaviconEdit" width="32" height="32" style="object-fit: contain; border: 1px solid #e0e0e0; border-radius: 4px;" />
                  <span class="text-caption text-grey">Preview (32×32)</span>
                  <v-btn icon variant="text" size="x-small" @click="siteFaviconEdit = ''">
                    <v-icon size="16">mdi-close</v-icon>
                  </v-btn>
                </div>
              </v-card-text>
              <v-card-actions class="pa-4 pt-2">
                <v-spacer />
                <v-btn variant="text" @click="showSettings = false">Cancel</v-btn>
                <v-btn color="primary" variant="flat" @click="saveSiteSettings">
                  Save
                </v-btn>
              </v-card-actions>
            </v-tabs-window-item>

            <!-- Domain tab -->
            <v-tabs-window-item value="domain">
              <v-card-text class="pa-4">
                <!-- Server IP instruction -->
                <v-alert
                  type="info"
                  variant="tonal"
                  density="compact"
                  class="mb-4"
                  border="start"
                >
                  <div class="text-body-2">
                    To connect a custom domain, add an <strong>A Record</strong> in your DNS settings:
                  </div>
                  <div class="mt-1">
                    <code>Type: A &nbsp;|&nbsp; Host: @ &nbsp;|&nbsp; Value: <strong>{{ serverIp || 'loading...' }}</strong></code>
                  </div>
                  <div class="text-caption text-grey mt-1">
                    DNS changes may take up to 24 hours to propagate.
                  </div>
                </v-alert>

                <!-- Add domain form -->
                <div class="d-flex align-center gap-2 mb-4">
                  <v-text-field
                    v-model="newDomainName"
                    label="Domain name"
                    placeholder="example.com"
                    variant="outlined"
                    density="compact"
                    hide-details="auto"
                    :error-messages="domainError"
                    @keyup.enter="handleAddDomain"
                  />
                  <v-btn
                    color="primary"
                    variant="flat"
                    :disabled="!newDomainName.trim() || domainLoading"
                    :loading="domainLoading"
                    @click="handleAddDomain"
                  >
                    Add
                  </v-btn>
                </div>

                <!-- Domains list -->
                <div v-if="siteDomains.length === 0" class="text-center py-6 text-grey">
                  <v-icon size="40" color="grey-lighten-2" class="mb-2">mdi-web</v-icon>
                  <div class="text-body-2">No custom domains connected</div>
                </div>

                <v-list v-else density="compact" class="pa-0">
                  <template v-for="(domain, idx) in siteDomains" :key="domain.id">
                    <v-list-item class="px-0">
                      <template #prepend>
                        <v-icon
                          :color="domain.isVerified ? 'success' : 'grey'"
                          size="20"
                          class="mr-3"
                        >
                          {{ domain.isVerified ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                        </v-icon>
                      </template>

                      <v-list-item-title class="text-body-2 font-weight-medium">
                        {{ domain.domainName }}
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        <v-chip
                          :color="domainStatusColor(domain)"
                          size="x-small"
                          variant="tonal"
                          class="mr-1"
                        >
                          {{ domain.isVerified ? 'Verified' : 'Not verified' }}
                        </v-chip>
                        <v-chip
                          v-if="domain.sslStatus && domain.sslStatus !== 'none'"
                          :color="sslStatusColor(domain.sslStatus)"
                          size="x-small"
                          variant="tonal"
                        >
                          SSL: {{ domain.sslStatus }}
                        </v-chip>
                      </v-list-item-subtitle>

                      <template #append>
                        <v-btn
                          variant="tonal"
                          size="x-small"
                          color="primary"
                          class="mr-1"
                          :loading="verifyingDomainId === domain.id"
                          @click="handleVerifyDomain(domain)"
                        >
                          <v-icon size="16" start>mdi-check-network</v-icon>
                          Verify
                        </v-btn>
                        <v-btn
                          variant="tonal"
                          size="x-small"
                          color="success"
                          class="mr-1"
                          :disabled="!domain.isVerified || domain.sslStatus === 'active'"
                          :loading="sslDomainId === domain.id"
                          @click="handleEnableSsl(domain)"
                        >
                          <v-icon size="16" start>mdi-lock</v-icon>
                          SSL
                        </v-btn>
                        <v-btn
                          icon
                          variant="text"
                          size="x-small"
                          color="error"
                          @click="handleRemoveDomain(domain)"
                        >
                          <v-icon size="18">mdi-delete</v-icon>
                        </v-btn>
                      </template>
                    </v-list-item>
                    <v-divider v-if="idx < siteDomains.length - 1" />
                  </template>
                </v-list>

                <!-- Verification result message -->
                <v-alert
                  v-if="verifyMessage"
                  :type="verifySuccess ? 'success' : 'warning'"
                  variant="tonal"
                  density="compact"
                  class="mt-4"
                  closable
                  @click:close="verifyMessage = ''"
                >
                  {{ verifyMessage }}
                </v-alert>

                <!-- SSL result message -->
                <v-alert
                  v-if="sslMessage"
                  :type="sslSuccess ? 'success' : 'error'"
                  variant="tonal"
                  density="compact"
                  class="mt-4"
                  closable
                  @click:close="sslMessage = ''"
                >
                  {{ sslMessage }}
                </v-alert>
              </v-card-text>
            </v-tabs-window-item>
          </v-tabs-window>
        </v-card>
      </v-dialog>
      <!-- Edit slug dialog -->
      <v-dialog v-model="showEditSlug" max-width="440" persistent>
        <v-card>
          <v-card-title class="pa-4">Page URL</v-card-title>
          <v-card-text class="pa-4 pt-0">
            <v-text-field
              v-model="editSlugValue"
              label="URL Path"
              variant="outlined"
              density="compact"
              prefix="/"
              hide-details="auto"
              autofocus
              placeholder="contact-us"
              @keyup.enter="saveSlug"
            />
            <div class="text-caption text-grey mt-2">
              Lowercase letters, numbers, hyphens. Example: <code>contact-us</code>
            </div>
          </v-card-text>
          <v-card-actions class="pa-4 pt-0">
            <v-spacer />
            <v-btn variant="text" @click="showEditSlug = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" @click="saveSlug">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

    <!-- Snackbar for notifications -->
    <v-snackbar v-model="showSnackbar" :color="snackbarColor" timeout="3000" location="bottom right">
      {{ snackbarText }}
    </v-snackbar>

    </v-container>
  </PublicLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSiteStore } from '@/stores/siteStore'
import type { IPage, IDomain } from '@/types/site'
import { slugify } from '@/utils/helpers'
import { addDomain, removeDomain, verifyDomain, enableSsl, fetchServerInfo, uploadFile } from '@/api/api'
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

// Edit slug inline
const showEditSlug = ref(false)
const editSlugPage = ref<IPage | null>(null)
const editSlugValue = ref('')

function editSlug(page: IPage) {
  editSlugPage.value = page
  // Strip common folder prefix artifact (e.g. 'folder/contact-us' → 'contact-us')
  const slug = page.slug || ''
  const segments = slug.split('/')
  const lastSegment = segments[segments.length - 1]
  editSlugValue.value = lastSegment !== undefined && lastSegment !== '' ? lastSegment : slug
  showEditSlug.value = true
}

async function saveSlug() {
  if (!siteStore.currentSite || !editSlugPage.value) return
  const cleanSlug = editSlugValue.value
    .trim()
    .replace(/^[\/]+|[\/]+$/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9-/]/g, '-')
  await siteStore.savePage(siteStore.currentSite.id, {
    ...editSlugPage.value,
    slug: cleanSlug,
  })
  showEditSlug.value = false
  editSlugPage.value = null
  notify('URL updated')
}

// Delete
const showDeleteConfirm = ref(false)
const deletingPage = ref<IPage | null>(null)

// Site settings
const showSettings = ref(false)
const settingsTab = ref('general')
const siteNameEdit = ref('')
const siteDescEdit = ref('')
const siteSubdomainEdit = ref('')
const siteFaviconEdit = ref('')
const faviconUploading = ref(false)
const faviconError = ref('')
const faviconInputRef = ref<HTMLInputElement | null>(null)

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
      siteFaviconEdit.value = url
    } else {
      faviconError.value = 'Upload failed'
    }
  } catch (err: any) {
    faviconError.value = err?.message || 'Upload failed'
  } finally {
    faviconUploading.value = false
  }
}

// Domain management
const serverIp = ref('')
const newDomainName = ref('')
const domainError = ref('')
const domainLoading = ref(false)
const verifyingDomainId = ref<string | null>(null)
const sslDomainId = ref<string | null>(null)
const verifyMessage = ref('')
const verifySuccess = ref(false)
const sslMessage = ref('')
const sslSuccess = ref(false)
const siteDomains = computed(() => siteStore.currentSite?.domains || [])

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
  // Preload server IP for domain tab
  loadServerIp()
})

// Populate site settings fields when site loads
watch(() => siteStore.currentSite, (site) => {
  if (site) {
    siteNameEdit.value = site.name
    siteDescEdit.value = site.description || ''
    siteSubdomainEdit.value = site.subdomain || ''
    siteFaviconEdit.value = site.favicon || ''
  }
}, { immediate: true })

function goBack() {
  router.push('/')
}

function openPageEditor(page: IPage) {
  if (!siteStore.currentSite) return
  router.push(`/editor/${siteStore.currentSite.id}/${page.id}`)
}

function openHtmlEditor(page: IPage) {
  if (!siteStore.currentSite) return
  router.push(`/html-editor/${siteStore.currentSite.id}/${page.id}`)
}

function openPagePreview(page: IPage) {
  if (!siteStore.currentSite) return
  router.push(`/preview/${siteStore.currentSite.id}/${page.id}`)
}

const isPublishing = ref(false)
const showSnackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

function notify(text: string, color = 'success') {
  snackbarText.value = text
  snackbarColor.value = color
  showSnackbar.value = true
}

async function publishSite() {
  if (!siteStore.currentSite) return
  isPublishing.value = true
  try {
    const success = await siteStore.publish()
    if (success) {
      notify('Site published successfully!', 'success')
    } else {
      notify('Failed to publish site', 'error')
    }
  } catch {
    notify('Failed to publish site', 'error')
  } finally {
    isPublishing.value = false
  }
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
    favicon: siteFaviconEdit.value,
  })
  showSettings.value = false
}

// ===== Domain Management =====

function domainStatusColor(domain: IDomain): string {
  return domain.isVerified ? 'success' : 'grey'
}

function sslStatusColor(status?: string): string {
  switch (status) {
    case 'active': return 'success'
    case 'pending': return 'warning'
    case 'error': return 'error'
    default: return 'grey'
  }
}

async function loadServerIp() {
  try {
    const info = await fetchServerInfo()
    serverIp.value = info.serverIp
  } catch {
    serverIp.value = ''
  }
}

async function handleAddDomain() {
  if (!siteStore.currentSite || !newDomainName.value.trim()) return
  domainError.value = ''
  domainLoading.value = true
  try {
    await addDomain(siteStore.currentSite.id, newDomainName.value.trim())
    newDomainName.value = ''
    // Reload site to get updated domains list
    await siteStore.loadSite(siteStore.currentSite.id)
  } catch (e: any) {
    domainError.value = e?.response?.data?.detail || 'Failed to add domain'
  } finally {
    domainLoading.value = false
  }
}

async function handleRemoveDomain(domain: IDomain) {
  if (!siteStore.currentSite || !domain.id) return
  await removeDomain(siteStore.currentSite.id, domain.id)
  await siteStore.loadSite(siteStore.currentSite.id)
}

async function handleVerifyDomain(domain: IDomain) {
  if (!siteStore.currentSite || !domain.id) return
  verifyingDomainId.value = domain.id
  verifyMessage.value = ''
  try {
    const result = await verifyDomain(siteStore.currentSite.id, domain.id)
    verifySuccess.value = result.isVerified
    verifyMessage.value = result.message
    // Reload to get updated verification status
    await siteStore.loadSite(siteStore.currentSite.id)
  } catch (e: any) {
    verifySuccess.value = false
    verifyMessage.value = e?.response?.data?.detail || 'Verification failed'
  } finally {
    verifyingDomainId.value = null
  }
}

async function handleEnableSsl(domain: IDomain) {
  if (!siteStore.currentSite || !domain.id) return
  sslDomainId.value = domain.id
  sslMessage.value = ''
  try {
    const result = await enableSsl(siteStore.currentSite.id, domain.id)
    sslSuccess.value = result.status === 'active'
    sslMessage.value = result.message
    // Reload to get updated SSL status
    await siteStore.loadSite(siteStore.currentSite.id)
  } catch (e: any) {
    sslSuccess.value = false
    sslMessage.value = e?.response?.data?.detail || 'SSL request failed'
  } finally {
    sslDomainId.value = null
  }
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
