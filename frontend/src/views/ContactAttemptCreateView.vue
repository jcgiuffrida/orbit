<template>
  <q-layout view="lHh Lpr lFf">
    <AppHeader @toggle-drawer="leftDrawerOpen = !leftDrawerOpen" />

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="q-pa-md" style="background-color: #f8f9fa;">
        <!-- Loading State -->
        <div v-if="isLoading" class="text-center q-pa-xl">
          <q-spinner-dots size="50px" color="primary" />
          <div class="q-mt-md">{{ isEditing ? 'Loading ping details...' : 'Loading...' }}</div>
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
              <q-breadcrumbs-el icon="contact_phone" label="Pings" @click="goToContactAttempts" class="cursor-pointer" />
              <q-breadcrumbs-el 
                v-if="isEditing && originalContactAttempt" 
                :label="`${originalContactAttempt.person_name || 'Ping'}`" 
                @click="goToPerson" 
                class="cursor-pointer" 
              />
              <q-breadcrumbs-el :label="isEditing ? 'Edit' : 'Add Ping'" />
            </q-breadcrumbs>
          </div>

          <div class="row justify-center">
            <div class="col-12 col-md-8 col-lg-6">
              <q-form @submit="saveContactAttempt" class="q-gutter-md" autocomplete="off">
                <!-- Main Information Card -->
                <q-card>
                  <q-card-section>
                    <div class="text-h6 q-mb-md">Ping Details</div>
                    
                    <!-- Person -->
                    <q-select
                      v-model="form.person"
                      :options="peopleOptions"
                      label="Person *"
                      filled
                      required
                      option-value="id"
                      option-label="name"
                      emit-value
                      map-options
                      autocomplete="off"
                      :rules="[val => !!val || 'Person is required']"
                      @popup-show="ensurePeopleLoaded"
                    >
                      <template v-slot:option="scope">
                        <q-item v-bind="scope.itemProps">
                          <q-item-section>
                            <q-item-label>{{ scope.opt.name }}</q-item-label>
                            <q-item-label v-if="scope.opt.name_ext" caption>{{ scope.opt.name_ext }}</q-item-label>
                          </q-item-section>
                        </q-item>
                      </template>
                    </q-select>

                    <div class="row q-col-gutter-sm">
                      <div class="col-7 col-sm-6">
                    
                        <!-- Type -->
                        <q-select
                          v-model="form.type"
                          :options="contactAttemptTypes"
                          label="Contact Type *"
                          filled
                          required
                          option-value="value"
                          option-label="label"
                          emit-value
                          map-options
                          autocomplete="off"
                          :rules="[val => !!val || 'Contact type is required']"
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
                      </div>

                      <div class="col">
                        <!-- Date -->
                        <q-input
                          v-model="form.date"
                          label="Date *"
                          type="date"
                          filled
                          required
                          autocomplete="off"
                          :rules="[val => !!val || 'Date is required']"
                        />
                      </div>
                    </div>
                    
                    <q-input
                      v-model="form.notes"
                      label="Notes"
                      type="textarea"
                      rows="2"
                      filled
                      autocomplete="off"
                      hint="What was the purpose? Any response or outcome?"
                      class="q-mb-md"
                    />
                    
                    <q-checkbox
                      v-model="form.ledToConversation"
                      label="This led to a conversation"
                      color="positive"
                    />

                    <br>
                    
                    <q-checkbox
                      v-model="form.private"
                      label="Private ping"
                      color="orange"
                    />
                    <div class="text-caption text-grey-6 q-ml-lg">
                      Private pings are only visible to you
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
                    :label="isEditing ? 'Save Changes' : 'Add Ping'"
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
import { useContactAttemptsStore } from '@/stores/contactAttempts'
import { usePeopleStore } from '@/stores/people'
import { contactAttemptTypes } from '@/services/contactAttempts'
import AppHeader from '@/components/AppHeader.vue'
import NavigationDrawer from '@/components/NavigationDrawer.vue'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const contactAttemptsStore = useContactAttemptsStore()
const peopleStore = usePeopleStore()

const leftDrawerOpen = ref(false)
const isLoading = ref(false)
const isSaving = ref(false)
const hasError = ref(false)
const error = ref(null)
const originalContactAttempt = ref(null)

const isEditing = computed(() => route.params.id && route.params.id !== 'new')

const form = reactive({
  person: '',
  date: new Date().toISOString().split('T')[0], // Today's date
  type: '',
  notes: '',
  ledToConversation: false,
  private: false
})

const resetForm = () => {
  form.person = ''
  form.date = new Date().toISOString().split('T')[0]
  form.type = ''
  form.notes = ''
  form.ledToConversation = false
  form.private = false
}

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
    // Always load people for the person selector
    await ensurePeopleLoaded()

    // Handle pre-population from query params
    if (route.query.person) {
      form.person = route.query.person
    }

    if (isEditing.value) {
      // Load existing contact attempt
      const contactAttemptId = route.params.id
      await contactAttemptsStore.fetchContactAttemptById(contactAttemptId)
      originalContactAttempt.value = contactAttemptsStore.selectedContactAttempt
      
      if (originalContactAttempt.value) {
        // Populate form with existing data
        form.person = originalContactAttempt.value.person
        form.date = originalContactAttempt.value.date
        form.type = originalContactAttempt.value.type
        form.notes = originalContactAttempt.value.notes || ''
        form.ledToConversation = !!originalContactAttempt.value.led_to_conversation
        form.private = originalContactAttempt.value.private || false
      }
    }
  } catch (err) {
    console.error('Failed to load data:', err)
    setError('Failed to load data')
  } finally {
    setLoading(false)
  }
}

const saveContactAttempt = async () => {
  isSaving.value = true
  
  try {
    const contactAttemptData = {
      person: form.person,
      date: form.date,
      type: form.type,
      notes: form.notes || '',
      led_to_conversation: form.ledToConversation,
      private: form.private,
    }
    
    if (isEditing.value) {
      // Update existing contact attempt
      const updatedContactAttempt = await contactAttemptsStore.updateContactAttempt(originalContactAttempt.value.id, contactAttemptData)
      
      $q.notify({
        type: 'positive',
        message: 'Ping updated successfully',
        position: 'top',
        timeout: 3000,
        actions: [{ icon: 'close', color: 'white', dense: true }]
      })
      
      // Navigate to contact attempts list
      router.push({ name: 'pings' })
    } else {
      // Create new contact attempt
      const newContactAttempt = await contactAttemptsStore.createContactAttempt(contactAttemptData)
      
      $q.notify({
        type: 'positive',
        message: 'Ping added successfully',
        position: 'top',
        timeout: 6000,
        actions: [
          { 
            icon: 'add', 
            color: 'white', 
            dense: true, 
            label: 'Add Another',
            handler: () => {
              // Reset form to add another ping
              resetForm()
              router.push({ name: 'ping-create' })
            }
          },
          { icon: 'close', color: 'white', dense: true }
        ]
      })
      
      // If user indicated it led to a conversation, offer to create one
      if (form.ledToConversation) {
        $q.dialog({
          title: 'Create Conversation',
          message: 'Would you like to record a conversation from this ping?',
          cancel: true,
          persistent: false
        }).onOk(() => {
          router.push({ 
            name: 'conversation-create', 
            query: { 
              participants: form.person,
              from_attempt: newContactAttempt.id,
              type: form.type === 'call' ? 'phone' : form.type,
              date: form.date
            }
          })
        }).onCancel(() => {
          router.push({ name: 'pings' })
        })
      } else {
        // Navigate to contact attempts list
        router.push({ name: 'pings' })
      }
    }
  } catch (err) {
    console.error('Failed to save contact attempt:', err)
    $q.notify({
      type: 'negative',
      message: `Failed to ${isEditing.value ? 'update' : 'create'} ping. Please try again.`,
      position: 'top',
      timeout: 4000
    })
  } finally {
    isSaving.value = false
  }
}

const cancelEdit = () => {
  router.push({ name: 'pings' })
}

const goToContactAttempts = () => {
  router.push({ name: 'pings' })
}

const goToPerson = () => {
  if (isEditing.value && originalContactAttempt.value) {
    router.push({ name: 'person-detail', params: { id: originalContactAttempt.value.person } })
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