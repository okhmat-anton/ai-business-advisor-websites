<template>
  <v-app>
    <AppHeader @toggle-drawer="drawer = !drawer" />

    <v-navigation-drawer v-model="drawer" app>
      <v-list density="compact" nav>
        <v-list-item
          prepend-icon="mdi-view-dashboard"
          title="Dashboard"
          to="/"
          rounded="lg"
        />
        <v-list-item
          prepend-icon="mdi-web"
          title="My Sites"
          to="/"
          rounded="lg"
        />
      </v-list>

      <template #append>
        <div class="pa-3">
          <v-btn
            block
            color="primary"
            variant="flat"
            prepend-icon="mdi-plus"
            @click="createNewSite"
          >
            New Site
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-main>
      <slot />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSiteStore } from '@/stores/siteStore'
import AppHeader from '@/components/common/AppHeader.vue'

const router = useRouter()
const siteStore = useSiteStore()
const drawer = ref(true)

async function createNewSite() {
  const site = await siteStore.addSite('New Website')
  if (site) {
    router.push(`/editor/${site.id}`)
  }
}
</script>
