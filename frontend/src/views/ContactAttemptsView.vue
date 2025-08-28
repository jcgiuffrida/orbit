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

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item clickable :to="{ name: 'home' }">
          <q-item-section avatar><q-icon name="home" /></q-item-section>
          <q-item-section>Home</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'people' }">
          <q-item-section avatar><q-icon name="people" /></q-item-section>
          <q-item-section>People</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'conversations' }">
          <q-item-section avatar><q-icon name="chat" /></q-item-section>
          <q-item-section>Conversations</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'contact-attempts' }">
          <q-item-section avatar><q-icon name="phone" /></q-item-section>
          <q-item-section>Contact Attempts</q-item-section>
        </q-item>
        <q-item clickable :to="{ name: 'relationships' }">
          <q-item-section avatar><q-icon name="favorite" /></q-item-section>
          <q-item-section>Relationships</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <q-page class="q-pa-md">
        <div class="text-h4 q-mb-md">Contact Attempts</div>
        <div class="text-body1">Contact attempts management coming soon...</div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'ContactAttemptsView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const leftDrawerOpen = ref(false)

    const handleLogout = async () => {
      await authStore.logout()
      router.push({ name: 'login' })
    }

    return {
      leftDrawerOpen,
      authStore,
      handleLogout
    }
  }
}
</script>