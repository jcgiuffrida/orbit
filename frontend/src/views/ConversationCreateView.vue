<template>
  <q-layout view="lHh Lpr lFf">
    <AppHeader @toggle-drawer="leftDrawerOpen = !leftDrawerOpen" />

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="q-pa-md" style="background-color: #f8f9fa;">
        <!-- Loading State -->
        <div v-if="isLoading" class="text-center q-pa-xl">
          <q-spinner-dots size="50px" color="primary" />
          <div class="q-mt-md">{{ isEditing ? 'Loading conversation details...' : 'Loading...' }}</div>
        </div>

        <!-- Error State -->
        <div v-else-if="hasError" class="text-center q-pa-xl">
          <q-icon name="error_outline" size="80px" color="negative" />
          <div class="text-h6 text-negative q-mt-md">
            {{ error }}
          </div>
          <q-btn 
            color="primary" 
            label="Try Again" 
            class="q-mt-md"
            @click="loadData"
          />
        </div>

        <!-- Create/Edit Form -->
        <div v-else>
          <!-- Breadcrumb Navigation -->
          <div class="breadcrumb-nav q-mb-md">
            <q-breadcrumbs class="text-grey-6">
              <q-breadcrumbs-el icon="chat" label="Conversations" @click="goToConversations" class="cursor-pointer" />
              <q-breadcrumbs-el 
                v-if="isEditing" 
                :label="originalConversation?.participants?.map(p => p.name).join(', ') || 'Conversation'" 
                @click="goToDetail" 
                class="cursor-pointer" 
              />
              <q-breadcrumbs-el :label="isEditing ? 'Edit' : 'Add Conversation'" />
            </q-breadcrumbs>
          </div>

          <div class="row justify-center">
            <div class="col-12 col-md-10 col-lg-8">
              <q-form @submit="saveConversation" class="q-gutter-md" autocomplete="off">
                <!-- Main Information Card -->
                <q-card>
                  <q-card-section>
                    <div class="text-h6 q-mb-md">Conversation Details</div>
                    
                    <!-- Participants -->
                    <q-select
                      v-model="form.participants"
                      :options="peopleOptions"
                      label="Participants *"
                      filled
                      multiple
                      required
                      option-value="id"
                      option-label="name"
                      emit-value
                      map-options
                      use-chips
                      stack-label
                      autocomplete="off"
                      class="q-mb-md"
                      :rules="[val => (val && val.length > 0) || 'At least one participant is required']"
                      @popup-show="ensurePeopleLoaded"
                    >
                      <template v-slot:selected-item="scope">
                        <q-chip
                          removable
                          @remove="scope.removeAtIndex(scope.index)"
                          :tabindex="scope.tabindex"
                          class="q-ma-xs"
                        >
                          {{ scope.opt.name }}
                        </q-chip>
                      </template>
                    </q-select>
                    
                    <!-- Date -->
                    <q-input
                      v-model="form.date"
                      label="Date *"
                      type="date"
                      filled
                      required
                      autocomplete="off"
                      class="q-mb-md"
                      :rules="[val => !!val || 'Date is required']"
                    />
                    
                    <!-- Type -->
                    <q-select
                      v-model="form.type"
                      :options="conversationTypes"
                      label="Conversation Type *"
                      filled
                      required
                      option-value="value"
                      option-label="label"
                      emit-value
                      map-options
                      autocomplete="off"
                      class="q-mb-md"
                      :rules="[val => !!val || 'Conversation type is required']"
                    >
                      <template v-slot:selected-item="scope">
                        <q-item-section avatar v-if="scope.opt.icon">
                          <q-icon :name="scope.opt.icon" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>{{ scope.opt.label }}</q-item-label>
                        </q-item-section>
                      </template>
                      <template v-slot:option="scope">
                        <q-item v-bind="scope.itemProps">
                          <q-item-section avatar v-if="scope.opt.icon">
                            <q-icon :name="scope.opt.icon" />
                          </q-item-section>
                          <q-item-section>
                            <q-item-label>{{ scope.opt.label }}</q-item-label>
                          </q-item-section>
                        </q-item>
                      </template>
                    </q-select>
                    
                    <!-- Location -->
                    <q-input
                      v-model="form.location"
                      label="Location"
                      hint="Where did this conversation take place?"
                      filled
                      autocomplete="off"
                      class="q-mb-md"
                    />
                  </q-card-section>
                </q-card>

                <!-- Notes Card -->
                <q-card>
                  <q-card-section>
                    <div class="text-h6 q-mb-md">Notes</div>
                    
                    <q-input
                      v-model="form.notes"
                      label="Conversation notes *"
                      type="textarea"
                      rows="6"
                      filled
                      required
                      autocomplete="off"
                      hint="What was discussed? Key topics, outcomes, follow-ups needed, etc."
                      class="q-mb-md"
                      :rules="[val => !!val || 'Notes are required']"
                    />
                  </q-card-section>
                </q-card>

                <!-- Privacy Settings Card -->
                <q-card>
                  <q-card-section>
                    <div class="text-h6 q-mb-md">Privacy Settings</div>
                    
                    <q-checkbox
                      v-model="form.private"
                      label="Private conversation"
                      color="orange"
                    />
                    <div class="text-caption text-grey-6 q-ml-lg">
                      Private conversations are only visible to you
                    </div>
                  </q-card-section>
                </q-card>

                <!-- Form Actions -->
                <div class="row q-gutter-sm justify-end q-mt-lg">
                  <q-btn 
                    flat 
                    label="Cancel" 
                    color="grey-7" 
                    @click="cancelEdit"
                  />
                  <q-btn 
                    type="submit" 
                    :label="isEditing ? 'Save Changes' : 'Add Conversation'"
                    color="primary"
                    :loading="isSaving"
                  />
                </div>
              </q-form>
            </div>
          </div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted, computed, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useConversationsStore } from '@/stores/conversations'
import { usePeopleStore } from '@/stores/people'
import { conversationTypes } from '@/services/conversations'
import AppHeader from '@/components/AppHeader.vue'
import NavigationDrawer from '@/components/NavigationDrawer.vue'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const conversationsStore = useConversationsStore()
const peopleStore = usePeopleStore()

const leftDrawerOpen = ref(false)
const isLoading = ref(false)
const isSaving = ref(false)
const hasError = ref(false)
const error = ref(null)
const originalConversation = ref(null)

const isEditing = computed(() => route.params.id && route.params.id !== 'new')

const form = reactive({
  participants: [],
  date: new Date().toISOString().split('T')[0], // Today's date
  type: '',
  location: '',
  notes: '',
  private: false
})

const peopleOptions = computed(() => peopleStore.getPeopleList)

const setLoading = (loading) => {
  isLoading.value = loading
  if (loading) {
    hasError.value = false
    error.value = null
  }
}

const setError = (err) => {
  hasError.value = true
  error.value = err
  isLoading.value = false
}

const ensurePeopleLoaded = async () => {
  if (peopleStore.getPeopleList.length === 0) {
    try {
      await peopleStore.fetchPeople()
    } catch (err) {
      console.error('Failed to load people:', err)
    }
  }
}

const loadData = async () => {
  setLoading(true)

  try {
    // Always load people for the participant selector
    await ensurePeopleLoaded()

    if (isEditing.value) {
      // Load existing conversation
      const conversationId = route.params.id
      await conversationsStore.fetchConversationById(conversationId)
      originalConversation.value = conversationsStore.selectedConversation
      
      if (originalConversation.value) {
        // Populate form with existing data
        form.participants = originalConversation.value.participants.map(p => p.id)
        form.date = originalConversation.value.date
        form.type = originalConversation.value.type
        form.location = originalConversation.value.location || ''
        form.notes = originalConversation.value.notes || ''
        form.private = originalConversation.value.private || false
      }
    } else {
      // Handle pre-populated data from query params (like follow-ups)
      if (route.query.participants) {
        form.participants = route.query.participants.split(',')
      }
    }
  } catch (err) {
    console.error('Failed to load data:', err)
    setError('Failed to load data')
  } finally {
    setLoading(false)
  }
}

const saveConversation = async () => {
  isSaving.value = true
  
  try {
    const conversationData = {
      participant_ids: form.participants,
      date: form.date,
      type: form.type,
      location: form.location || '',
      notes: form.notes,
      private: form.private
    }
    
    if (isEditing.value) {
      // Update existing conversation
      const updatedConversation = await conversationsStore.updateConversation(originalConversation.value.id, conversationData)
      
      $q.notify({
        type: 'positive',
        message: 'Conversation updated successfully',
        position: 'top',
        timeout: 3000,
        actions: [{ icon: 'close', color: 'white', dense: true }]
      })
      
      // Navigate to detail view
      router.push({ name: 'conversation-detail', params: { id: updatedConversation.id } })
    } else {
      // Create new conversation
      const newConversation = await conversationsStore.createConversation(conversationData)
      
      $q.notify({
        type: 'positive',
        message: 'Conversation added successfully',
        position: 'top',
        timeout: 3000,
        actions: [{ icon: 'close', color: 'white', dense: true }]
      })
      
      // Navigate to detail view
      router.push({ name: 'conversation-detail', params: { id: newConversation.id } })
    }
  } catch (err) {
    console.error('Failed to save conversation:', err)
    $q.notify({
      type: 'negative',
      message: `Failed to ${isEditing.value ? 'update' : 'create'} conversation. Please try again.`,
      position: 'top',
      timeout: 4000
    })
  } finally {
    isSaving.value = false
  }
}

const cancelEdit = () => {
  if (isEditing.value && originalConversation.value) {
    router.push({ name: 'conversation-detail', params: { id: originalConversation.value.id } })
  } else {
    router.push({ name: 'conversations' })
  }
}

const goToConversations = () => {
  router.push({ name: 'conversations' })
}

const goToDetail = () => {
  if (isEditing.value && originalConversation.value) {
    router.push({ name: 'conversation-detail', params: { id: originalConversation.value.id } })
  }
}

// Watch for route parameter changes
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadData()
  }
})

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.q-form .q-card {
  margin-bottom: 24px;
}

.q-form .q-card:last-of-type {
  margin-bottom: 0;
}

.breadcrumb-nav .q-breadcrumbs-el--link {
  opacity: 0.8;
  transition: opacity 0.2s;
}

.breadcrumb-nav .q-breadcrumbs-el--link:hover {
  opacity: 1;
}
</style>