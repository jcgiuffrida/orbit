<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat round dense icon="arrow_back" @click="goBack" />
        <q-toolbar-title>
          {{ person?.name || 'Person Details' }}
        </q-toolbar-title>
        <q-space />
        <q-btn flat round dense icon="logout" @click="handleLogout" />
      </q-toolbar>
    </q-header>

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="q-pa-md">
        <!-- Loading State -->
        <div v-if="peopleStore.isLoading" class="text-center q-pa-xl">
          <q-spinner-dots size="50px" color="primary" />
          <div class="q-mt-md">Loading person details...</div>
        </div>

        <!-- Error State -->
        <div v-else-if="peopleStore.hasError" class="text-center q-pa-xl">
          <q-icon name="error_outline" size="80px" color="negative" />
          <div class="text-h6 text-negative q-mt-md">
            {{ peopleStore.error }}
          </div>
          <q-btn 
            color="primary" 
            label="Try Again" 
            class="q-mt-md"
            @click="loadPerson"
          />
        </div>

        <!-- Person Not Found -->
        <div v-else-if="!person" class="text-center q-pa-xl">
          <q-icon name="person_off" size="80px" color="grey-5" />
          <div class="text-h6 text-grey-7 q-mt-md">
            Person not found
          </div>
          <q-btn 
            color="primary" 
            label="Back to People" 
            class="q-mt-md"
            @click="goBack"
          />
        </div>

        <!-- Person Details -->
        <div v-else>
          <!-- Header Section -->
          <div class="row q-mb-lg">
            <div class="col">
              <div class="text-h4 q-mb-xs">{{ person.name }}</div>
              <div v-if="person.name_ext" class="text-h6 text-grey-7 q-mb-sm">
                {{ person.name_ext }}
              </div>
              <div class="text-caption text-grey-6">
                Added {{ formatDate(person.created_at) }}
                <span v-if="person.created_by_username">
                  by {{ person.created_by_username }}
                </span>
              </div>
            </div>
            <div class="col-auto">
              <q-btn-group>
                <q-btn 
                  color="primary" 
                  icon="edit" 
                  label="Edit"
                  @click="editPerson"
                />
                <q-btn 
                  color="negative" 
                  icon="delete" 
                  label="Delete"
                  @click="showDeleteDialog = true"
                />
              </q-btn-group>
            </div>
          </div>

          <!-- Main Content -->
          <div class="row q-gutter-lg">
            <!-- Left Column - Basic Info -->
            <div class="col-12 col-md-6">
              <q-card class="q-mb-md">
                <q-card-section>
                  <div class="text-h6 q-mb-md">Contact Information</div>
                  
                  <div v-if="person.email" class="q-mb-sm">
                    <div class="text-caption text-grey-7">Email</div>
                    <div class="text-body1">
                      <q-icon name="email" size="16px" class="q-mr-xs" />
                      {{ person.email }}
                      <q-btn 
                        flat 
                        dense 
                        round 
                        size="sm" 
                        icon="content_copy" 
                        @click="copyEmail"
                        class="q-ml-xs"
                      >
                        <q-tooltip>Copy Email</q-tooltip>
                      </q-btn>
                    </div>
                  </div>

                  <div v-if="person.phone" class="q-mb-sm">
                    <div class="text-caption text-grey-7">Phone</div>
                    <div class="text-body1">
                      <q-icon name="phone" size="16px" class="q-mr-xs" />
                      {{ person.phone }}
                      <q-btn 
                        flat 
                        dense 
                        round 
                        size="sm" 
                        icon="sms" 
                        @click="textPerson"
                        class="q-ml-xs"
                      >
                        <q-tooltip>Send Text</q-tooltip>
                      </q-btn>
                    </div>
                  </div>

                  <div v-if="person.location" class="q-mb-sm">
                    <div class="text-caption text-grey-7">Location</div>
                    <div class="text-body1">
                      <q-icon name="place" size="16px" class="q-mr-xs" />
                      {{ person.location }}
                    </div>
                  </div>

                  <div v-if="person.birthday" class="q-mb-sm">
                    <div class="text-caption text-grey-7">Birthday</div>
                    <div class="text-body1">
                      <q-icon name="cake" size="16px" class="q-mr-xs" />
                      {{ formatBirthday(person.birthday) }}
                    </div>
                  </div>

                  <div v-if="person.last_contacted" class="q-mb-sm">
                    <div class="text-caption text-grey-7">Last Contact</div>
                    <div class="text-body1 text-positive">
                      <q-icon name="schedule" size="16px" class="q-mr-xs" />
                      {{ formatDate(person.last_contacted) }}
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- How We Met -->
              <q-card v-if="person.how_we_met" class="q-mb-md">
                <q-card-section>
                  <div class="text-h6 q-mb-md">How We Met</div>
                  <div class="text-body1">{{ person.how_we_met }}</div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Right Column - Notes & AI Summary -->
            <div class="col-12 col-md-6">
              <q-card v-if="person.notes" class="q-mb-md">
                <q-card-section>
                  <div class="text-h6 q-mb-md">Notes</div>
                  <div class="text-body1 pre-line">{{ person.notes }}</div>
                </q-card-section>
              </q-card>

              <q-card v-if="person.ai_summary" class="q-mb-md">
                <q-card-section>
                  <div class="text-h6 q-mb-md">AI Summary</div>
                  <div class="text-body1 pre-line">{{ person.ai_summary }}</div>
                </q-card-section>
              </q-card>

              <!-- Quick Actions -->
              <q-card class="q-mb-md">
                <q-card-section>
                  <div class="text-h6 q-mb-md">Quick Actions</div>
                  <div class="row q-gutter-sm">
                    <q-btn 
                      color="primary" 
                      icon="chat_bubble" 
                      label="Log Conversation"
                      @click="addConversation"
                    />
                    <q-btn 
                      v-if="person.email"
                      color="info" 
                      icon="email" 
                      label="Copy Email"
                      @click="copyEmail"
                    />
                    <q-btn 
                      v-if="person.phone"
                      color="positive" 
                      icon="sms" 
                      label="Send Text"
                      @click="textPerson"
                    />
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>

        <!-- Delete Confirmation Dialog -->
        <q-dialog v-model="showDeleteDialog" persistent>
          <q-card>
            <q-card-section class="row items-center">
              <q-avatar icon="warning" color="negative" text-color="white" />
              <span class="q-ml-sm">
                Are you sure you want to delete <strong>{{ person?.name }}</strong>? 
                This action cannot be undone.
              </span>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancel" color="primary" @click="showDeleteDialog = false" />
              <q-btn flat label="Delete" color="negative" @click="confirmDelete" />
            </q-card-actions>
          </q-card>
        </q-dialog>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/auth'
import { usePeopleStore } from '@/stores/people'
import NavigationDrawer from '@/components/NavigationDrawer.vue'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const authStore = useAuthStore()
const peopleStore = usePeopleStore()

const leftDrawerOpen = ref(false)
const showDeleteDialog = ref(false)

// Get person from store
const person = computed(() => peopleStore.selectedPerson)

// Methods
const loadPerson = async () => {
  const personId = route.params.id
  if (personId) {
    try {
      await peopleStore.fetchPersonById(personId)
    } catch (error) {
      console.error('Failed to load person:', error)
    }
  }
}

const goBack = () => {
  router.push({ name: 'people' })
}

const editPerson = () => {
  // TODO: Navigate to edit view
  console.log('Edit person:', person.value)
}

const confirmDelete = async () => {
  if (!person.value) return

  try {
    const personName = person.value.name
    await peopleStore.deletePerson(person.value.id)
    showDeleteDialog.value = false
    
    $q.notify({
      type: 'negative',
      message: `🗑️ ${personName} deleted successfully`,
      position: 'top',
      timeout: 4000,
      actions: [{ icon: 'close', color: 'white', dense: true }]
    })
    
    // Navigate back to people list
    router.push({ name: 'people' })
  } catch (error) {
    console.error('Failed to delete person:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to delete person. Please try again.',
      position: 'top',
      timeout: 4000
    })
  }
}

const copyEmail = async () => {
  if (!person.value?.email) return

  try {
    await navigator.clipboard.writeText(person.value.email)
    $q.notify({
      type: 'positive',
      message: `Email copied: ${person.value.email}`,
      position: 'top',
      timeout: 3000,
      actions: [{ icon: 'close', color: 'white', dense: true }]
    })
  } catch (error) {
    console.error('Failed to copy email:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to copy email address',
      position: 'top',
      timeout: 3000
    })
  }
}

const textPerson = () => {
  if (person.value?.phone) {
    window.open(`sms:${person.value.phone}`)
    $q.notify({
      type: 'info',
      message: `Opening SMS to ${person.value.name}`,
      position: 'top',
      timeout: 2000
    })
  }
}

const addConversation = () => {
  // TODO: Navigate to add conversation with person pre-selected
  console.log('Add conversation with:', person.value)
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = now - date
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) {
    return diffDays === 1 ? '1 day ago' : `${diffDays} days ago`
  }
  if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7)
    return weeks === 1 ? '1 week ago' : `${weeks} weeks ago`
  }
  if (diffDays < 365) {
    const months = Math.floor(diffDays / 30)
    return months === 1 ? '1 month ago' : `${months} months ago`
  }
  return date.toLocaleDateString()
}

const formatBirthday = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, { 
    month: 'long', 
    day: 'numeric',
    year: 'numeric'
  })
}

const handleLogout = async () => {
  await authStore.logout()
  $q.notify({
    type: 'info',
    message: '👋 Logged out successfully',
    position: 'top',
    timeout: 2000
  })
  router.push({ name: 'login' })
}

// Lifecycle
onMounted(() => {
  loadPerson()
})
</script>

<style scoped>
.pre-line {
  white-space: pre-line;
}
</style>