<template>
  <q-header elevated>
    <q-toolbar>
      <q-btn flat round dense icon="menu" @click="toggleDrawer" />
      <q-toolbar-title class="cursor-pointer" @click="goHome">
        Orbit
      </q-toolbar-title>
      <q-space />
      <q-btn flat round dense icon="logout" @click="handleLogout" />
    </q-toolbar>
  </q-header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/auth'

const emit = defineEmits(['toggle-drawer'])
const router = useRouter()
const $q = useQuasar()
const authStore = useAuthStore()

const toggleDrawer = () => {
  emit('toggle-drawer')
}

const goHome = () => {
  router.push({ name: 'home' })
}

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