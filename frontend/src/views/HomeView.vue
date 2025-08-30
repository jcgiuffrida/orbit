<template>
  <q-layout view="lHh Lpr lFf">
    <AppHeader @toggle-drawer="leftDrawerOpen = !leftDrawerOpen" />

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
import AppHeader from '@/components/AppHeader.vue'
import NavigationDrawer from '@/components/NavigationDrawer.vue'

const leftDrawerOpen = ref(false)
</script>