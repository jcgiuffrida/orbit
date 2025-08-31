<template>
  <q-layout view="lHh Lpr lFf">
    <AppHeader @toggle-drawer="leftDrawerOpen = !leftDrawerOpen" />

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="q-pa-md" style="background-color: #f8f9fa;">
        <!-- Loading State -->
        <div v-if="conversationsStore.isLoading" class="text-center q-pa-xl">
          <q-spinner-dots size="50px" color="primary" />
          <div class="q-mt-md">Loading conversation details...</div>
        </div>

        <!-- Error State -->
        <div v-else-if="conversationsStore.hasError" class="text-center q-pa-xl">
          <q-icon name="error_outline" size="80px" color="negative" />
          <div class="text-h6 text-negative q-mt-md">
            {{ conversationsStore.error }}
          </div>
          <q-btn 
            color="primary" 
            label="Try Again" 
            class="q-mt-md"
            @click="loadConversation"
          />
        </div>

        <!-- Conversation Not Found -->
        <div v-else-if="!conversation" class="text-center q-pa-xl">
          <q-icon name="chat_bubble_outline" size="80px" color="grey-5" />
          <div class="text-h6 text-grey-7 q-mt-md">
            Conversation not found
          </div>
          <q-btn 
            color="primary" 
            label="Back to Conversations" 
            class="q-mt-md"
            @click="goBack"
          />
        </div>

        <!-- Conversation Details -->
        <div v-else class="conversation-detail-container">
          <!-- Breadcrumb Navigation -->
          <div class="breadcrumb-nav q-mb-md">
            <q-breadcrumbs class="text-grey-6">
              <q-breadcrumbs-el icon="chat" label="Conversations" @click="goBack" class="cursor-pointer" />
              <q-breadcrumbs-el :label="`${getParticipantNames(conversation.participants)} - ${formatDateLong(conversation.date)}`" />
            </q-breadcrumbs>
          </div>

          <!-- Header Section -->
          <q-card class="header-card q-mb-lg" flat>
            <q-card-section class="q-pa-lg">
              <div class="row items-start q-gutter-md">
                <div class="col-auto">
                  <q-avatar size="64px" :color="getTypeColor(conversation.type)" text-color="white">
                    <q-icon :name="getTypeIcon(conversation.type)" size="32px" />
                  </q-avatar>
                </div>
                <div class="col">
                  <div class="row items-center q-gutter-sm q-mb-sm">
                    <div class="text-h5 text-weight-medium">{{ getParticipantNames(conversation.participants) }}</div>
                    <q-chip 
                      :color="getTypeColor(conversation.type)" 
                      text-color="white"
                      :icon="getTypeIcon(conversation.type)"
                    >
                      {{ getTypeLabel(conversation.type) }}
                    </q-chip>
                    <q-chip v-if="conversation.private" color="orange" text-color="white" icon="lock">
                      Private
                    </q-chip>
                  </div>
                  <div class="text-body1 text-grey-8 q-mb-sm">
                    {{ formatDateLong(conversation.date) }}
                    <span v-if="conversation.location"> • {{ conversation.location }}</span>
                  </div>
                  <div class="text-body2 text-grey-6">
                    <q-icon name="schedule" size="16px" class="q-mr-xs" />
                    Added {{ formatDate(conversation.created_at) }}
                    <span v-if="conversation.created_by_username">
                      by {{ conversation.created_by_username }}
                    </span>
                  </div>
                </div>
                <div class="col-auto">
                  <div class="action-buttons">
                    <q-btn 
                      outline
                      color="primary" 
                      icon="edit" 
                      label="Edit"
                      class="q-mr-sm"
                      @click="editConversation"
                    />
                    <q-btn 
                      outline
                      color="positive" 
                      icon="add_comment" 
                      label="Follow-up"
                      class="q-mr-sm"
                      @click="followUpConversation"
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
            <!-- Left Column - Details -->
            <div class="col-12 col-md-4">
              <!-- Conversation Details Card -->
              <q-card class="content-card q-mb-lg" flat bordered>
                <q-card-section class="q-pa-lg">
                  <div class="text-h6 q-mb-md text-weight-medium">Details</div>
                  
                  <div class="detail-item q-mb-md">
                    <div class="row items-center q-gutter-sm">
                      <q-icon :name="getTypeIcon(conversation.type)" size="20px" :color="getTypeColor(conversation.type)" />
                      <div class="col">
                        <div class="text-body1">{{ getTypeLabel(conversation.type) }}</div>
                      </div>
                    </div>
                  </div>

                  <div class="detail-item q-mb-md">
                    <div class="row items-center q-gutter-sm">
                      <q-icon name="event" size="20px" color="grey-7" />
                      <div class="col">
                        <div class="text-body1">{{ formatDateLong(conversation.date) }}</div>
                      </div>
                    </div>
                  </div>

                  <div v-if="conversation.location" class="detail-item q-mb-md">
                    <div class="row items-center q-gutter-sm">
                      <q-icon name="place" size="20px" color="grey-7" />
                      <div class="col">
                        <div class="text-body1">{{ conversation.location }}</div>
                      </div>
                    </div>
                  </div>

                  <div class="detail-item">
                    <div class="row items-center q-gutter-sm">
                      <q-icon :name="conversation.private ? 'lock' : 'public'" size="20px" :color="conversation.private ? 'orange' : 'positive'" />
                      <div class="col">
                        <div class="text-body1">{{ conversation.private ? 'Private' : 'Shared' }}</div>
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- Participants Card (only show if more than one participant) -->
              <q-card class="content-card" flat bordered>
                <q-card-section class="q-pa-lg">
                  <div class="text-h6 q-mb-md text-weight-medium">Participants</div>
                  <div 
                    v-for="participant in conversation.participants" 
                    :key="participant.id"
                    class="participant-item"
                  >
                    <div class="row items-center q-gutter-sm cursor-pointer" @click="viewParticipant(participant)">
                      <q-avatar size="32px" color="grey-4" text-color="grey-8">
                        <q-icon name="person" />
                      </q-avatar>
                      <div class="col">
                        <div class="text-body2 text-weight-medium">{{ participant.name }}</div>
                        <div v-if="participant.name_ext" class="text-caption text-grey-6">
                          {{ participant.name_ext }}
                        </div>
                      </div>
                      <q-icon name="chevron_right" color="grey-5" />
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Right Column - Notes -->
            <div class="col-12 col-md-8">
              <q-card class="content-card" flat bordered>
                <q-card-section class="q-pa-lg">
                  <div class="text-h6 q-mb-md text-weight-medium">Notes</div>
                  <div class="text-body1 text-grey-8 pre-line conversation-notes">
                    {{ conversation.notes }}
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>

        <!-- Delete Confirmation Dialog -->
        <q-dialog v-model="showDeleteDialog">
          <q-card>
            <q-card-section class="row items-center">
              <q-avatar icon="warning" color="negative" text-color="white" />
              <span class="q-ml-sm">
                Are you sure you want to delete this conversation with <strong>{{ conversation ? getParticipantNames(conversation.participants) : '' }}</strong>? 
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
import { useConversationsStore } from '@/stores/conversations'
import { getConversationTypeIcon, getConversationTypeLabel } from '@/services/conversations'
import AppHeader from '@/components/AppHeader.vue'
import NavigationDrawer from '@/components/NavigationDrawer.vue'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const conversationsStore = useConversationsStore()

const leftDrawerOpen = ref(false)
const showDeleteDialog = ref(false)

const conversation = computed(() => conversationsStore.selectedConversation)

const getParticipantNames = (participants) => {
  if (!participants || participants.length === 0) return 'Unknown'
  return participants.map(p => p.name).join(', ')
}

const getTypeIcon = (type) => getConversationTypeIcon(type)
const getTypeLabel = (type) => getConversationTypeLabel(type)

const getTypeColor = (type) => {
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

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = now - date
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
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

const formatDateLong = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = now - date
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return `Today, ${date.toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })}`
  } else if (diffDays === 1) {
    return `Yesterday, ${date.toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })}`
  } else if (diffDays < 7) {
    return date.toLocaleDateString(undefined, { 
      weekday: 'long',
      month: 'long', 
      day: 'numeric',
      year: 'numeric'
    })
  } else {
    return date.toLocaleDateString(undefined, { 
      weekday: 'long',
      year: 'numeric',
      month: 'long', 
      day: 'numeric'
    })
  }
}

const loadConversation = async () => {
  const conversationId = route.params.id
  if (conversationId) {
    try {
      await conversationsStore.fetchConversationById(conversationId)
    } catch (error) {
      console.error('Failed to load conversation:', error)
    }
  }
}

const goBack = () => {
  router.push({ name: 'conversations' })
}

const editConversation = () => {
  if (conversation.value) {
    router.push({ name: 'conversation-edit', params: { id: conversation.value.id } })
  }
}

const followUpConversation = () => {
  if (conversation.value) {
    const participantIds = conversation.value.participants.map(p => p.id)
    router.push({ 
      name: 'conversation-create', 
      query: { participants: participantIds.join(','), followup: conversation.value.id } 
    })
  }
}

const viewParticipant = (participant) => {
  router.push({ name: 'person-detail', params: { id: participant.id } })
}

const confirmDelete = async () => {
  if (!conversation.value) return

  try {
    const participantNames = getParticipantNames(conversation.value.participants)
    await conversationsStore.deleteConversation(conversation.value.id)
    showDeleteDialog.value = false
    
    $q.notify({
      type: 'positive',
      message: `Conversation with ${participantNames} deleted successfully`,
      position: 'top',
      timeout: 4000,
      actions: [{ icon: 'close', color: 'white', dense: true }]
    })
    
    // Navigate back to conversations list
    router.push({ name: 'conversations' })
  } catch (error) {
    console.error('Failed to delete conversation:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to delete conversation. Please try again.',
      position: 'top',
      timeout: 4000
    })
  }
}

// Watch for route parameter changes
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadConversation()
  }
})

onMounted(() => {
  loadConversation()
})
</script>

<style scoped>
.pre-line {
  white-space: pre-line;
}

.conversation-detail-container {
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

.participant-item,
.detail-item {
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.participant-item:last-child,
.detail-item:last-child {
  border-bottom: none;
}

.participant-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.action-buttons .q-btn {
  min-width: 100px;
}

.conversation-notes {
  line-height: 1.6;
  font-size: 15px;
}
</style>