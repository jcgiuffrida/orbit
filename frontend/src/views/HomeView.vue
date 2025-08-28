<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-toolbar-title>
          Orbit
        </q-toolbar-title>
        <div>Hello, {{ authStore.user?.username }}</div>
        <q-space />
        <q-btn flat round dense icon="logout" @click="handleLogout" />
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      class="bg-grey-1"
    >
      <q-list>
        <q-item-label header>Navigation</q-item-label>
        <q-item clickable v-ripple :to="{ name: 'people' }">
          <q-item-section avatar>
            <q-icon name="people" />
          </q-item-section>
          <q-item-section>People</q-item-section>
        </q-item>
        <q-item clickable v-ripple :to="{ name: 'conversations' }">
          <q-item-section avatar>
            <q-icon name="chat" />
          </q-item-section>
          <q-item-section>Conversations</q-item-section>
        </q-item>
        <q-item clickable v-ripple :to="{ name: 'contact-attempts' }">
          <q-item-section avatar>
            <q-icon name="phone" />
          </q-item-section>
          <q-item-section>Contact Attempts</q-item-section>
        </q-item>
        <q-item clickable v-ripple :to="{ name: 'relationships' }">
          <q-item-section avatar>
            <q-icon name="favorite" />
          </q-item-section>
          <q-item-section>Relationships</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

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

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'HomeView',
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