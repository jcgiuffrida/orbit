<template>
  <q-drawer :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" show-if-above bordered class="bg-grey-1">
    <q-list>
      <q-item 
        v-for="item in navigationItems" 
        :key="item.name"
        clickable 
        v-ripple 
        :to="{ name: item.name }"
        :active="isActive(item.name)"
        active-class="text-primary bg-grey-3"
      >
        <q-item-section avatar>
          <q-icon :name="item.icon" />
        </q-item-section>
        <q-item-section>{{ item.label }}</q-item-section>
      </q-item>
    </q-list>
  </q-drawer>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:modelValue'])

const route = useRoute()

const navigationItems = [
  { name: 'home', label: 'Home', icon: 'home' },
  { name: 'people', label: 'People', icon: 'people' },
  { name: 'conversations', label: 'Conversations', icon: 'chat' },
  { name: 'contact-attempts', label: 'Contact Attempts', icon: 'phone' }
]

const isActive = computed(() => (routeName) => {
  return route.name === routeName
})
</script>