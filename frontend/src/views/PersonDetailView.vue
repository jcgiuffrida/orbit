<template>
  <q-layout view="lHh Lpr lFf">
    <AppHeader @toggle-drawer="leftDrawerOpen = !leftDrawerOpen" />

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="q-pa-md" style="background-color: #f8f9fa;">
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
        <div v-else class="person-detail-container">
          <!-- Breadcrumb Navigation -->
          <div class="breadcrumb-nav q-mb-md">
            <q-breadcrumbs class="text-grey-6">
              <q-breadcrumbs-el icon="people" label="People" @click="goBack" class="cursor-pointer" />
              <q-breadcrumbs-el :label="person.name" />
            </q-breadcrumbs>
          </div>

          <!-- Header Section -->
          <q-card class="header-card q-mb-lg" flat>
            <q-card-section class="q-pa-lg">
              <div class="row items-start q-gutter-md">
                <div class="col">
                  <div class="text-h4 q-mb-sm text-weight-medium">{{ person.name }}</div>
                  <div v-if="person.name_ext" class="text-h6 text-grey-7 q-mb-md">
                    {{ person.name_ext }}
                  </div>
                  <div class="text-body2 text-grey-6">
                    <q-icon name="schedule" size="16px" class="q-mr-xs" />
                    Added {{ formatDate(person.created_at) }}
                    <span v-if="person.created_by_username">
                      by {{ person.created_by_username }}
                    </span>
                  </div>
                </div>
                <div class="col-auto">
                  <div class="action-buttons">
                    <q-btn 
                      color="primary" 
                      icon="chat_bubble" 
                      label="Log Conversation"
                      class="q-mr-sm"
                      @click="addConversation"
                    />
                    <q-btn 
                      outline
                      color="primary" 
                      icon="edit" 
                      label="Edit"
                      class="q-mr-sm"
                      @click="editPerson"
                    />
                    <q-btn 
                      outline
                      color="negative" 
                      icon="delete" 
                      label="Delete"
                      @click="showDeleteDialog = true"
                    />
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Main Content -->
          <div class="row q-col-gutter-lg">
            <!-- Left Column - Contact Info -->
            <div class="col-12 col-md-6">
              <q-card class="content-card q-mb-lg" flat bordered>
                <q-card-section class="q-pa-lg">
                  <div class="text-h6 q-mb-md text-weight-medium">Contact Information</div>

                  <div v-if="person.location" class="contact-item q-mb-md">
                    <div class="row items-center q-gutter-sm">
                      <q-icon name="place" size="20px" color="grey-7" />
                      <div class="col text-body1">{{ person.location }}</div>
                    </div>
                  </div>
                  
                  <div v-if="person.email" class="contact-item q-mb-md">
                    <div class="row items-center q-gutter-sm">
                      <q-icon name="email" size="20px" color="grey-7" />
                      <div class="col text-body1">{{ person.email }}</div>
                      <q-btn 
                        unelevated
                        size="sm" 
                        icon="content_copy" 
                        color="info"
                        text-color="white"
                        @click="copyEmail"
                        class="contact-action-btn"
                      >
                        <q-tooltip>Copy Email</q-tooltip>
                      </q-btn>
                    </div>
                  </div>

                  <div v-if="person.phone" class="contact-item q-mb-md">
                    <div class="row items-center q-gutter-sm">
                      <q-icon name="phone" size="20px" color="grey-7" />
                      <div class="col text-body1">{{ person.phone }}</div>
                      <q-btn 
                        unelevated
                        size="sm" 
                        icon="sms" 
                        color="positive"
                        text-color="white"
                        @click="textPerson"
                        class="contact-action-btn"
                      >
                        <q-tooltip>Send Text</q-tooltip>
                      </q-btn>
                    </div>
                  </div>

                  <div v-if="person.birthday" class="contact-item q-mb-md">
                    <div class="row items-center q-gutter-sm">
                      <q-icon name="cake" size="20px" color="grey-7" />
                      <div class="col">
                        <div class="text-body1">{{ formatBirthday(person.birthday) }}</div>
                        <div class="text-caption text-grey-6">Birthday</div>
                      </div>
                    </div>
                  </div>

                  <div v-if="person.last_contacted" class="contact-item q-mb-md">
                    <div class="row items-center q-gutter-sm">
                      <q-icon name="schedule" size="20px" color="positive" />
                      <div class="col">
                        <div class="text-body1 text-positive">{{ formatDate(person.last_contacted) }}</div>
                        <div class="text-caption text-grey-6">Last Contact</div>
                      </div>
                    </div>
                  </div>

                  <!-- How We Met - De-emphasized -->
                  <div v-if="person.how_we_met" class="contact-item">
                    <div class="row items-start q-gutter-sm">
                      <q-icon name="handshake" size="18px" color="grey-6" />
                      <div class="col">
                        <div class="text-body2 text-grey-7">{{ person.how_we_met }}</div>
                        <div class="text-caption text-grey-5">How we met</div>
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- Notes -->
              <q-card v-if="person.notes" class="content-card q-mb-lg" flat bordered>
                <q-card-section class="q-pa-lg">
                  <div class="text-h6 q-mb-md text-weight-medium">Notes</div>
                  <div class="text-body1 text-grey-8 pre-line">{{ person.notes }}</div>
                </q-card-section>
              </q-card>

              <!-- AI Summary -->
              <q-card v-if="person.ai_summary" class="content-card" flat bordered>
                <q-card-section class="q-pa-lg">
                  <div class="text-h6 q-mb-md text-weight-medium">AI Summary</div>
                  <div class="text-body1 text-grey-8 pre-line ai-summary-text">{{ person.ai_summary }}</div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Right Column - Conversations -->
            <div class="col-12 col-md-6">
              <!-- Conversations -->
              <q-card class="content-card q-mb-lg" flat bordered>
                <q-card-section class="q-pa-lg">
                  <div class="text-h6 q-mb-md text-weight-medium">Conversations</div>
                  
                  <!-- Loading State -->
                  <div v-if="loadingConversations" class="text-center q-pa-md">
                    <q-spinner-dots size="20px" color="primary" />
                    <div class="text-caption text-grey-6 q-mt-sm">Loading conversations...</div>
                  </div>
                  
                  <!-- No conversations -->
                  <div v-else-if="personConversations.length === 0" class="text-center q-pa-md">
                    <q-icon name="chat_bubble_outline" size="32px" color="grey-4" />
                    <div class="text-body2 text-grey-6 q-mt-sm">No conversations recorded yet</div>
                  </div>
                  
                  <!-- Conversations List -->
                  <div v-else class="conversations-scroll-container">
                    <div 
                      v-for="conversation in personConversations" 
                      :key="conversation.id"
                      class="conversation-timeline-item q-mb-sm cursor-pointer"
                      @click="viewConversation(conversation)"
                    >
                      <div class="row items-start q-gutter-sm">
                        <q-avatar size="32px" :color="getConversationTypeColor(conversation.type)" text-color="white">
                          <q-icon :name="getConversationTypeIcon(conversation.type)" size="16px" />
                        </q-avatar>
                        <div class="col">
                          <div class="text-body2 text-weight-medium q-mb-xs">
                            {{ getConversationTypeLabel(conversation.type) }}
                            <span v-if="conversation.location"> • {{ conversation.location }}</span>
                          </div>
                          <div class="text-caption text-grey-6 q-mb-xs">
                            {{ formatConversationDate(conversation.date) }}
                          </div>
                          <div class="text-body2 text-grey-7 conversation-preview">
                            {{ truncateText(conversation.notes, 100) }}
                          </div>
                        </div>
                        <q-icon name="chevron_right" color="grey-4" size="16px" />
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- Relationships -->
              <PersonRelationships 
                :key="person.id"
                :person-id="person.id"
                :person-name="person.name"
              />
            </div>
          </div>
        </div>

        <!-- Delete Confirmation Dialog -->
        <q-dialog v-model="showDeleteDialog">
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
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { usePeopleStore } from '@/stores/people'
import { useConversationsStore } from '@/stores/conversations'
import { getConversationTypeIcon, getConversationTypeLabel } from '@/services/conversations'
import AppHeader from '@/components/AppHeader.vue'
import NavigationDrawer from '@/components/NavigationDrawer.vue'
import PersonRelationships from '@/components/PersonRelationships.vue'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const peopleStore = usePeopleStore()
const conversationsStore = useConversationsStore()

const leftDrawerOpen = ref(false)
const showDeleteDialog = ref(false)
const loadingConversations = ref(false)
const personConversations = ref([])

// Get person from store
const person = computed(() => peopleStore.selectedPerson)

// Methods
const loadPerson = async () => {
  const personId = route.params.id
  if (personId) {
    try {
      await peopleStore.fetchPersonById(personId)
      // Also load conversations for this person
      await loadConversations()
    } catch (error) {
      console.error('Failed to load person:', error)
    }
  }
}

const loadConversations = async () => {
  if (!person.value) return
  
  loadingConversations.value = true
  try {
    const conversations = await conversationsStore.fetchConversationsForPerson(person.value.id)
    personConversations.value = conversations
  } catch (error) {
    console.error('Failed to load conversations:', error)
    personConversations.value = []
  } finally {
    loadingConversations.value = false
  }
}

const goBack = () => {
  router.push({ name: 'people' })
}

const editPerson = () => {
  if (person.value) {
    router.push({ name: 'person-edit', params: { id: person.value.id } })
  }
}

const confirmDelete = async () => {
  if (!person.value) return

  try {
    const personName = person.value.name
    await peopleStore.deletePerson(person.value.id)
    showDeleteDialog.value = false
    
    $q.notify({
      type: 'negative',
      message: `${personName} deleted successfully`,
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
  if (person.value) {
    router.push({ 
      name: 'conversation-create', 
      query: { participants: person.value.id } 
    })
  }
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

const formatConversationDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = now - date
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  return date.toLocaleDateString(undefined, { 
    weekday: 'short',
    month: 'short', 
    day: 'numeric'
  })
}

const truncateText = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}

const getConversationTypeColor = (type) => {
  const colors = {
    'in_person': 'primary',
    'phone': 'positive',
    'text': 'info',
    'email': 'secondary',
    'video': 'accent',
    'other': 'grey-6'
  }
  return colors[type] || 'grey-6'
}

const viewConversation = (conversation) => {
  router.push({ name: 'conversation-detail', params: { id: conversation.id } })
}


// Watch for route parameter changes
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadPerson()
  }
})

// Lifecycle
onMounted(() => {
  loadPerson()
})
</script>

<style scoped>
.pre-line {
  white-space: pre-line;
}

.person-detail-container {
  max-width: 1400px;
  margin: 0 auto;
}

.breadcrumb-nav .q-breadcrumbs-el--link {
  opacity: 0.8;
  transition: opacity 0.2s;
}

.breadcrumb-nav .q-breadcrumbs-el--link:hover {
  opacity: 1;
}

.header-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.content-card {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.2s ease;
}

.content-card:hover {
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
}

.contact-item {
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.contact-item:last-child {
  border-bottom: none;
}

.action-buttons .q-btn {
  min-width: 120px;
}

.contact-item .q-icon {
  min-width: 24px;
}

.conversation-timeline-item {
  padding: 12px;
  border-radius: 8px;
  transition: background-color 0.2s ease;
}

.conversation-timeline-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.conversation-preview {
  line-height: 1.4;
}

.contact-action-btn {
  min-width: 36px;
  border-radius: 6px;
  font-weight: 500;
}

.conversations-scroll-container {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 4px;
}

.conversations-scroll-container::-webkit-scrollbar {
  width: 4px;
}

.conversations-scroll-container::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 2px;
}

.conversations-scroll-container::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 2px;
}

.conversations-scroll-container::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

.ai-summary-text {
  font-style: italic;
}
</style>