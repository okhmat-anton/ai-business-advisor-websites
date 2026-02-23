<template>
  <v-app-bar color="white" elevation="0" density="compact" class="app-header">
    <v-app-bar-nav-icon variant="text" @click="$emit('toggle-drawer')" />

    <v-toolbar-title class="text-subtitle-1 font-weight-bold">
      <router-link to="/" class="text-decoration-none text-black">
        AKM Site Builder
      </router-link>
    </v-toolbar-title>

    <v-spacer />

    <v-btn icon variant="text" size="small">
      <v-icon>mdi-bell-outline</v-icon>
    </v-btn>

    <v-menu>
      <template #activator="{ props }">
        <v-btn icon variant="text" v-bind="props">
          <v-avatar size="32" color="primary">
            <span class="text-white text-caption">
              {{ userInitials }}
            </span>
          </v-avatar>
        </v-btn>
      </template>
      <v-list density="compact">
        <v-list-item prepend-icon="mdi-account" title="Profile" />
        <v-list-item prepend-icon="mdi-cog" title="Settings" />
        <v-divider />
        <v-list-item
          prepend-icon="mdi-logout"
          title="Logout"
          @click="logout"
        />
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'

defineEmits<{
  'toggle-drawer': []
}>()

const authStore = useAuthStore()

const userInitials = computed(() => {
  const name = authStore.userName || 'User'
  return name
    .split(' ')
    .map((n: string) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

function logout() {
  authStore.logout()
}
</script>

<style scoped>
.app-header {
  border-bottom: 1px solid #e0e0e0;
}
</style>
