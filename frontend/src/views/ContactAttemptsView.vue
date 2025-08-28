<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat round dense icon="menu" @click="leftDrawerOpen = !leftDrawerOpen" />
        <q-toolbar-title>Contact Attempts</q-toolbar-title>
        <q-space />
        <q-btn flat round dense icon="logout" @click="handleLogout" />
      </q-toolbar>
    </q-header>

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="q-pa-md">
        <div class="text-h4 q-mb-md">Contact Attempts</div>
        <div class="text-body1">Contact attempts management coming soon...</div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NavigationDrawer from '@/components/NavigationDrawer.vue'

const router = useRouter()
const authStore = useAuthStore()
const leftDrawerOpen = ref(false)

const handleLogout = async () => {
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>