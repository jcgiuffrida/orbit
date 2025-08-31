<template>
  <q-layout view="lHh Lpr lFf">
    <AppHeader @toggle-drawer="leftDrawerOpen = !leftDrawerOpen" />

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="q-pa-md" style="background-color: #f8f9fa;">
        <!-- Header -->
        <div class="row items-center q-mb-lg">
          <div class="text-h4 col">Contact Attempts</div>
          <q-btn 
            color="primary" 
            icon="add" 
            label="Add Contact Attempt" 
            @click="addContactAttempt" 
          />
        </div>

        <!-- Search and Sorting -->
        <div class="row q-col-gutter-md q-mb-lg">
          <div class="col-12 col-md-6">
            <q-input
              v-model="searchQuery"
              filled
              placeholder="Search contact attempts..."
              clearable
            >
              <template v-slot:prepend>
                <q-icon name="search" />
              </template>
            </q-input>
          </div>
          <div class="col-12 col-md-3">
            <q-select
              v-model="filterType"
              filled
              :options="typeFilterOptions"
              label="Filter by type"
              emit-value
              map-options
              clearable
            />
          </div>
          <div class="col-12 col-md-3">
            <q-select
              v-model="sortBy"
              filled
              :options="sortOptions"
              label="Sort by"
              emit-value
              map-options
            />
          </div>
        </div>

        <!-- Contact Attempts Timeline -->
        <div v-if="contactAttemptsStore.isLoading" class="text-center q-pa-lg">
          <q-spinner-dots size="50px" color="primary" />
          <div class="q-mt-md">Loading contact attempts...</div>
        </div>

        <div v-else-if="contactAttemptsStore.hasError" class="text-center q-pa-xl">
          <q-icon name="error_outline" size="80px" color="negative" />
          <div class="text-h6 text-negative q-mt-md">
            {{ contactAttemptsStore.error }}
          </div>
          <q-btn 
            color="primary" 
            label="Try Again" 
            class="q-mt-md"
            @click="loadContactAttempts"
          />
        </div>

        <div v-else-if="filteredContactAttempts.length === 0" class="text-center q-pa-xl">
          <q-icon name="contact_phone" size="80px" color="grey-5" />
          <div class="text-h6 text-grey-7 q-mt-md">
            {{ searchQuery || filterType ? 'No contact attempts found matching your criteria' : 'No contact attempts recorded yet' }}
          </div>
          <q-btn 
            v-if="!searchQuery && !filterType"
            color="primary" 
            label="Add Your First Contact Attempt" 
            class="q-mt-md"
            @click="addContactAttempt"
          />
        </div>

        <!-- Timeline Layout -->
        <div v-else class="timeline-container">
          <div 
            v-for="attempt in filteredContactAttempts" 
            :key="attempt.id"
            class="timeline-item q-mb-md"
          >
            <div class="timeline-marker">
              <q-avatar size="40px" :color="getTypeColor(attempt.type)" text-color="white">
                <q-icon :name="getTypeIcon(attempt.type)" size="20px" />
              </q-avatar>
            </div>
            <q-card class="timeline-card cursor-pointer" @click="viewContactAttempt(attempt)">
              <q-card-section>
                <div class="row items-start justify-between">
                  <div class="col">
                    <div class="row items-center q-gutter-sm q-mb-sm">
                      <div class="text-h6 text-weight-medium">{{ attempt.person_name || 'Unknown Person' }}</div>
                      <q-chip 
                        size="sm" 
                        :color="getTypeColor(attempt.type)" 
                        text-color="white"
                        :icon="getTypeIcon(attempt.type)"
                      >
                        {{ getTypeLabel(attempt.type) }}
                      </q-chip>
                      <q-chip v-if="attempt.private" size="sm" color="orange" text-color="white" icon="lock">
                        Private
                      </q-chip>
                    </div>
                    <div class="text-body2 text-grey-8 q-mb-sm">
                      {{ formatDate(attempt.date) }}
                      <q-tooltip>
                        {{ formatDateLong(attempt.date) }}
                      </q-tooltip>
                    </div>
                    <div v-if="attempt.notes" class="text-body2 text-grey-7">
                      {{ truncateText(attempt.notes, 150) }}
                    </div>
                    <div v-if="attempt.led_to_conversation" class="text-caption text-positive q-mt-sm">
                      <q-icon name="arrow_forward" size="14px" class="q-mr-xs" />
                      Led to conversation
                    </div>
                  </div>
                  <div class="col-auto">
                    <q-btn 
                      flat 
                      round 
                      size="sm" 
                      icon="more_vert" 
                      @click.stop="showContactAttemptMenu($event, attempt)"
                    >
                      <q-menu>
                        <q-list style="min-width: 100px">
                          <q-item clickable v-close-popup @click="editContactAttempt(attempt)">
                            <q-item-section avatar>
                              <q-icon name="edit" />
                            </q-item-section>
                            <q-item-section>Edit</q-item-section>
                          </q-item>
                          <q-item clickable v-close-popup @click="addConversation(attempt)">
                            <q-item-section avatar>
                              <q-icon name="chat_bubble" />
                            </q-item-section>
                            <q-item-section>Add Conversation</q-item-section>
                          </q-item>
                          <q-separator />
                          <q-item clickable v-close-popup @click="deleteContactAttempt(attempt)">
                            <q-item-section avatar>
                              <q-icon name="delete" color="negative" />
                            </q-item-section>
                            <q-item-section class="text-negative">Delete</q-item-section>
                          </q-item>
                        </q-list>
                      </q-menu>
                    </q-btn>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useContactAttemptsStore } from '@/stores/contactAttempts'
import { contactAttemptTypes, getContactAttemptTypeIcon, getContactAttemptTypeLabel, getContactAttemptTypeColor } from '@/services/contactAttempts'
import { formatDate, formatDateLong } from '@/utils/dateFormatting'
import AppHeader from '@/components/AppHeader.vue'
import NavigationDrawer from '@/components/NavigationDrawer.vue'

const router = useRouter()
const $q = useQuasar()
const contactAttemptsStore = useContactAttemptsStore()

const leftDrawerOpen = ref(false)
const searchQuery = ref('')
const filterType = ref('')
const sortBy = ref('-date')

const typeFilterOptions = [
  ...contactAttemptTypes,
  { label: 'All Types', value: '' }
]

const sortOptions = [
  { label: 'Most Recent', value: '-date' },
  { label: 'Oldest First', value: 'date' },
  { label: 'Type', value: 'type' },
  { label: 'Person (A-Z)', value: 'person_name' }
]

const filteredContactAttempts = computed(() => {
  let filtered = [...contactAttemptsStore.getContactAttemptsList]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(attempt => {
      const personName = (attempt.person_name || '').toLowerCase()
      const notes = (attempt.notes || '').toLowerCase()
      return personName.includes(query) || notes.includes(query)
    })
  }

  if (filterType.value) {
    filtered = filtered.filter(attempt => attempt.type === filterType.value)
  }

  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'date':
        return new Date(a.date) - new Date(b.date)
      case '-date':
        return new Date(b.date) - new Date(a.date)
      case 'type':
        return getContactAttemptTypeLabel(a.type).localeCompare(getContactAttemptTypeLabel(b.type))
      case 'person_name':
        return (a.person_name || '').localeCompare(b.person_name || '')
      default:
        return 0
    }
  })

  return filtered
})

const getTypeIcon = (type) => getContactAttemptTypeIcon(type)
const getTypeLabel = (type) => getContactAttemptTypeLabel(type)

const getTypeColor = (type) => getContactAttemptTypeColor(type)

const truncateText = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}

const loadContactAttempts = async () => {
  try {
    await contactAttemptsStore.fetchContactAttempts()
  } catch (error) {
    console.error('Error loading contact attempts:', error)
  }
}

const viewContactAttempt = (attempt) => {
  router.push({ name: 'contact-attempt-detail', params: { id: attempt.id } })
}

const addContactAttempt = () => {
  router.push({ name: 'contact-attempt-create' })
}

const editContactAttempt = (attempt) => {
  router.push({ name: 'contact-attempt-edit', params: { id: attempt.id } })
}

const addConversation = (attempt) => {
  // Navigate to conversation create with pre-filled data from the attempt
  router.push({ 
    name: 'conversation-create', 
    query: { 
      participants: attempt.person,
      from_attempt: attempt.id,
    }
  })
}

const deleteContactAttempt = async (attempt) => {
  $q.dialog({
    title: 'Delete Contact Attempt',
    message: `Are you sure you want to delete this contact attempt with ${attempt.person_name}?`,
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await contactAttemptsStore.deleteContactAttempt(attempt.id)
      $q.notify({
        type: 'positive',
        message: 'Contact attempt deleted successfully',
        position: 'top',
        timeout: 3000
      })
    } catch (error) {
      console.error('Failed to delete contact attempt:', error)
      $q.notify({
        type: 'negative',
        message: 'Failed to delete contact attempt. Please try again.',
        position: 'top',
        timeout: 4000
      })
    }
  })
}

const showContactAttemptMenu = (event, attempt) => {
  // Menu is handled by the template
}

onMounted(() => {
  loadContactAttempts()
})
</script>

<style scoped>
.timeline-container {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
}

.timeline-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.timeline-marker {
  position: relative;
  z-index: 2;
  flex-shrink: 0;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: 20px;
  top: 50px;
  bottom: -20px;
  width: 2px;
  background: rgba(0, 0, 0, 0.1);
  z-index: 1;
}

.timeline-item:last-child::before {
  display: none;
}

.timeline-card {
  flex: 1;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid rgba(0,0,0,0.08);
  background: white;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.04);
}

.timeline-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}
</style>