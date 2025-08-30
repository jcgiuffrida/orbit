<template>
  <q-layout view="lHh Lpr lFf">
    <AppHeader @toggle-drawer="leftDrawerOpen = !leftDrawerOpen" />

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="q-pa-md" style="background-color: #f8f9fa;">
        <!-- Header -->
        <div class="row items-center q-mb-lg">
          <div class="text-h4 col">Conversations</div>
          <q-btn 
            color="primary" 
            icon="add" 
            label="Add Conversation" 
            @click="addConversation" 
          />
        </div>

        <!-- Search and Sorting -->
        <div class="row q-col-gutter-md q-mb-lg">
          <div class="col-12 col-md-6">
            <q-input
              v-model="searchQuery"
              filled
              placeholder="Search conversations..."
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

        <!-- Conversations List -->
        <div v-if="conversationsStore.isLoading" class="text-center q-pa-lg">
          <q-spinner-dots size="50px" color="primary" />
          <div class="q-mt-md">Loading conversations...</div>
        </div>

        <div v-else-if="conversationsStore.hasError" class="text-center q-pa-xl">
          <q-icon name="error_outline" size="80px" color="negative" />
          <div class="text-h6 text-negative q-mt-md">
            {{ conversationsStore.error }}
          </div>
          <q-btn 
            color="primary" 
            label="Try Again" 
            class="q-mt-md"
            @click="loadConversations"
          />
        </div>

        <div v-else-if="filteredConversations.length === 0" class="text-center q-pa-xl">
          <q-icon name="chat_bubble_outline" size="80px" color="grey-5" />
          <div class="text-h6 text-grey-7 q-mt-md">
            {{ searchQuery || filterType ? 'No conversations found matching your criteria' : 'No conversations recorded yet' }}
          </div>
          <q-btn 
            v-if="!searchQuery && !filterType"
            color="primary" 
            label="Add Your First Conversation" 
            class="q-mt-md"
            @click="addConversation"
          />
        </div>

        <div v-else class="row q-col-gutter-md">
          <div 
            v-for="conversation in filteredConversations" 
            :key="conversation.id"
            class="col-12"
          >
            <q-card class="conversation-card cursor-pointer" @click="viewConversation(conversation)">
              <q-card-section>
                <div class="row items-start q-gutter-md">
                  <div class="col-auto">
                    <q-avatar size="48px" :color="getTypeColor(conversation.type)" text-color="white">
                      <q-icon :name="getTypeIcon(conversation.type)" size="24px" />
                    </q-avatar>
                  </div>
                  <div class="col">
                    <div class="row items-center q-gutter-sm q-mb-xs">
                      <div class="text-h6">{{ getParticipantNames(conversation.participants) }}</div>
                      <q-chip 
                        size="sm" 
                        :color="getTypeColor(conversation.type)" 
                        text-color="white"
                        :icon="getTypeIcon(conversation.type)"
                      >
                        {{ getTypeLabel(conversation.type) }}
                      </q-chip>
                      <q-chip v-if="conversation.private" size="sm" color="orange" text-color="white" icon="lock">
                        Private
                      </q-chip>
                    </div>
                    <div class="text-body2 text-grey-8 q-mb-sm">
                      {{ formatDate(conversation.date) }}
                      <span v-if="conversation.location"> • {{ conversation.location }}</span>
                    </div>
                    <div class="text-body2 text-grey-7 conversation-notes">
                      {{ truncateText(conversation.notes, 150) }}
                    </div>
                  </div>
                  <div class="col-auto">
                    <q-btn 
                      flat 
                      round 
                      size="sm" 
                      icon="more_vert" 
                      @click.stop="showConversationMenu($event, conversation)"
                    >
                      <q-menu>
                        <q-list style="min-width: 100px">
                          <q-item clickable v-close-popup @click="editConversation(conversation)">
                            <q-item-section avatar>
                              <q-icon name="edit" />
                            </q-item-section>
                            <q-item-section>Edit</q-item-section>
                          </q-item>
                          <q-item clickable v-close-popup @click="followUpConversation(conversation)">
                            <q-item-section avatar>
                              <q-icon name="add_comment" />
                            </q-item-section>
                            <q-item-section>Follow-up</q-item-section>
                          </q-item>
                          <q-separator />
                          <q-item clickable v-close-popup @click="deleteConversation(conversation)">
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
import { useConversationsStore } from '@/stores/conversations'
import { conversationTypes, getConversationTypeIcon, getConversationTypeLabel } from '@/services/conversations'
import AppHeader from '@/components/AppHeader.vue'
import NavigationDrawer from '@/components/NavigationDrawer.vue'

const router = useRouter()
const $q = useQuasar()
const conversationsStore = useConversationsStore()

const leftDrawerOpen = ref(false)
const searchQuery = ref('')
const filterType = ref('')
const sortBy = ref('-date')

const typeFilterOptions = [
  ...conversationTypes,
  { label: 'All Types', value: '' }
]

const sortOptions = [
  { label: 'Most Recent', value: '-date' },
  { label: 'Oldest First', value: 'date' },
  { label: 'Type', value: 'type' },
  { label: 'Participants (A-Z)', value: 'participants' }
]

const filteredConversations = computed(() => {
  let filtered = [...conversationsStore.getConversationsList]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(conversation => {
      const participantNames = getParticipantNames(conversation.participants).toLowerCase()
      const notes = conversation.notes.toLowerCase()
      const location = conversation.location?.toLowerCase() || ''
      return participantNames.includes(query) || 
             notes.includes(query) || 
             location.includes(query)
    })
  }

  if (filterType.value) {
    filtered = filtered.filter(conversation => conversation.type === filterType.value)
  }

  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'date':
        return new Date(a.date) - new Date(b.date)
      case '-date':
        return new Date(b.date) - new Date(a.date)
      case 'type':
        return getConversationTypeLabel(a.type).localeCompare(getConversationTypeLabel(b.type))
      case 'participants':
        return getParticipantNames(a.participants).localeCompare(getParticipantNames(b.participants))
      default:
        return 0
    }
  })

  return filtered
})

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
  if (!dateString) return ''
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

const truncateText = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}

const loadConversations = async () => {
  try {
    await conversationsStore.fetchConversations()
  } catch (error) {
    console.error('Error loading conversations:', error)
  }
}

const viewConversation = (conversation) => {
  router.push({ name: 'conversation-detail', params: { id: conversation.id } })
}

const addConversation = () => {
  router.push({ name: 'conversation-create' })
}

const editConversation = (conversation) => {
  router.push({ name: 'conversation-edit', params: { id: conversation.id } })
}

const followUpConversation = (conversation) => {
  const participantIds = conversation.participants.map(p => p.id)
  router.push({ 
    name: 'conversation-create', 
    query: { participants: participantIds.join(','), followup: conversation.id } 
  })
}

const deleteConversation = async (conversation) => {
  $q.dialog({
    title: 'Delete Conversation',
    message: `Are you sure you want to delete this conversation with ${getParticipantNames(conversation.participants)}?`,
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await conversationsStore.deleteConversation(conversation.id)
      $q.notify({
        type: 'negative',
        message: 'Conversation deleted successfully',
        position: 'top',
        timeout: 3000
      })
    } catch (error) {
      console.error('Failed to delete conversation:', error)
      $q.notify({
        type: 'negative',
        message: 'Failed to delete conversation. Please try again.',
        position: 'top',
        timeout: 4000
      })
    }
  })
}

const showConversationMenu = (event, conversation) => {
  // Menu is handled by the template
}

onMounted(() => {
  loadConversations()
})
</script>

<style scoped>
.conversation-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid rgba(0,0,0,0.08);
  background: white;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.04);
}

.conversation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.conversation-notes {
  white-space: pre-line;
  line-height: 1.4;
}
</style>