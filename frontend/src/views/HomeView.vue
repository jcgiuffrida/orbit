<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-toolbar-title>
          Orbit
        </q-toolbar-title>
        <q-space />
        <q-btn flat round dense icon="logout" @click="handleLogout" />
      </q-toolbar>
    </q-header>

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="flex flex-center">
        <div class="text-center">
          <h1 class="text-h6 q-mb-md">Welcome to Orbit</h1>
          <p class="text-body1">Track your personal connections and conversations.</p>
          <q-btn-group class="q-mt-lg">
            <q-btn color="primary" :to="{ name: 'people' }" label="View People" />
            <q-btn color="secondary" :to="{ name: 'conversations' }" label="View Conversations" />
          </q-btn-group>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/auth'
import NavigationDrawer from '@/components/NavigationDrawer.vue'

const router = useRouter()
const $q = useQuasar()
const authStore = useAuthStore()
const leftDrawerOpen = ref(false)

const handleLogout = async () => {
  await authStore.logout()
  $q.notify({
    type: 'info',
    message: 'Logged out successfully',
    position: 'top',
    timeout: 2000
  })
  router.push({ name: 'login' })
}
</script>