<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat round dense icon="close" @click="cancelEdit" />
        <q-toolbar-title>
          {{ isCreating ? 'Add Person' : `Edit ${originalPerson?.name || 'Person'}` }}
        </q-toolbar-title>
        <q-space />
        <q-btn flat round dense icon="logout" @click="handleLogout" />
      </q-toolbar>
    </q-header>

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="q-pa-md" style="background-color: #f8f9fa;">
        <!-- Loading State -->
        <div v-if="peopleStore.isLoading && !isCreating" class="text-center q-pa-xl">
          <q-spinner-dots size="50px" color="primary" />
          <div class="q-mt-md">Loading person details...</div>
        </div>

        <!-- Error State -->
        <div v-else-if="peopleStore.hasError && !isCreating" class="text-center q-pa-xl">
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

        <!-- Edit Form -->
        <div v-else>
          <!-- Breadcrumb Navigation -->
          <div class="breadcrumb-nav q-mb-md">
            <q-breadcrumbs class="text-grey-6">
              <q-breadcrumbs-el icon="people" label="People" @click="goToPeople" class="cursor-pointer" />
              <q-breadcrumbs-el 
                v-if="!isCreating" 
                :label="originalPerson?.name || 'Person'" 
                @click="goToDetail" 
                class="cursor-pointer" 
              />
              <q-breadcrumbs-el :label="isCreating ? 'Add Person' : 'Edit'" />
            </q-breadcrumbs>
          </div>

          <div class="row justify-center">
            <div class="col-12 col-md-8 col-lg-6">
              <q-form @submit="savePerson" class="q-gutter-md" autocomplete="off">
                <!-- Basic Information Card -->
                <q-card>
                  <q-card-section>
                    <div class="text-h6 q-mb-md">Basic Information</div>
                    
                    <q-input
                      v-model="form.name"
                      label="Full name *"
                      filled
                      required
                      autocomplete="off"
                      class="q-mb-md"
                      :rules="[val => !!val || 'Name is required']"
                    />
                    
                    <q-input
                      v-model="form.name_ext"
                      label="Additional context"
                      hint="e.g. Luca's dad"
                      filled
                      autocomplete="off"
                      class="q-mb-md"
                    />
                    
                    <q-input
                      v-model="form.location"
                      label="Location"
                      hint="City or state"
                      filled
                      autocomplete="off"
                      class="q-mb-md"
                    />
                  </q-card-section>
                </q-card>

                <!-- Contact Information Card -->
                <q-card>
                  <q-card-section>
                    <div class="text-h6 q-mb-md">Contact Information</div>
                    
                    <q-input
                      v-model="form.email"
                      label="Email"
                      type="email"
                      filled
                      autocomplete="off"
                      class="q-mb-md"
                    />
                    
                    <q-input
                      v-model="form.phone"
                      label="Phone"
                      type="tel"
                      filled
                      autocomplete="off"
                      class="q-mb-md"
                    />
                    
                    <q-input
                      v-model="form.birthday"
                      label="Birthday"
                      type="date"
                      filled
                      autocomplete="off"
                      class="q-mb-md"
                    />
                    
                  </q-card-section>
                </q-card>

                <!-- Additional Information Card -->
                <q-card>
                  <q-card-section>
                    <div class="text-h6 q-mb-md">Additional Information</div>
                    
                    <q-input
                      v-model="form.how_we_met"
                      label="How we met"
                      filled
                      autocomplete="off"
                      class="q-mb-md"
                    />
                    
                    <q-input
                      v-model="form.notes"
                      label="Notes"
                      type="textarea"
                      rows="4"
                      filled
                      autocomplete="off"
                      class="q-mb-md"
                    />
                    
                    <q-input
                      v-model="form.ai_summary"
                      label="AI Summary"
                      type="textarea"
                      rows="3"
                      filled
                      autocomplete="off"
                      class="q-mb-md"
                      hint="AI-generated summary of conversations and interactions"
                    />
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
                    :label="isCreating ? 'Add Person' : 'Save Changes'"
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
import { ref, onMounted, computed, reactive } from 'vue'
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
const isSaving = ref(false)
const originalPerson = ref(null)

// Determine if we're creating or editing
const isCreating = computed(() => route.params.id === 'new')

// Form data
const form = reactive({
  name: '',
  name_ext: '',
  email: '',
  phone: '',
  location: '',
  birthday: '',
  how_we_met: '',
  notes: '',
  ai_summary: ''
})

// Methods
const loadPerson = async () => {
  if (isCreating.value) return

  const personId = route.params.id
  if (personId) {
    try {
      await peopleStore.fetchPersonById(personId)
      originalPerson.value = peopleStore.selectedPerson
      
      // Populate form with existing data
      if (originalPerson.value) {
        Object.keys(form).forEach(key => {
          form[key] = originalPerson.value[key] || ''
        })
        
        // Format dates for input fields
        if (originalPerson.value.birthday) {
          form.birthday = formatDateForInput(originalPerson.value.birthday)
        }
      }
    } catch (error) {
      console.error('Failed to load person:', error)
    }
  }
}

const formatDateForInput = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toISOString().split('T')[0]
}

const savePerson = async () => {
  isSaving.value = true
  
  try {
    // Prepare form data - send empty strings as-is, backend expects them
    const personData = { ...form }
    if (!personData.birthday) {
      personData.birthday = null
    }
    
    if (isCreating.value) {
      // Create new person
      const newPerson = await peopleStore.createPerson(personData)
      
      $q.notify({
        type: 'positive',
        message: `Person ${newPerson.name} created successfully`,
        position: 'top',
        timeout: 3000,
        actions: [{ icon: 'close', color: 'white', dense: true }]
      })
      
      // Navigate to the new person's detail page
      router.push({ name: 'person-detail', params: { id: newPerson.id } })
    } else {
      // Update existing person
      const updatedPerson = await peopleStore.updatePerson(originalPerson.value.id, personData)
      
      $q.notify({
        type: 'positive',
        message: `${updatedPerson.name} updated successfully`,
        position: 'top',
        timeout: 3000,
        actions: [{ icon: 'close', color: 'white', dense: true }]
      })
      
      // Navigate back to detail view
      router.push({ name: 'person-detail', params: { id: originalPerson.value.id } })
    }
  } catch (error) {
    console.error('Failed to save person:', error)
    $q.notify({
      type: 'negative',
      message: `Failed to ${isCreating.value ? 'create' : 'update'} person. Please try again.`,
      position: 'top',
      timeout: 4000
    })
  } finally {
    isSaving.value = false
  }
}

const cancelEdit = () => {
  if (isCreating.value) {
    router.push({ name: 'people' })
  } else {
    router.push({ name: 'person-detail', params: { id: route.params.id } })
  }
}

const goToPeople = () => {
  router.push({ name: 'people' })
}

const goToDetail = () => {
  if (!isCreating.value && route.params.id) {
    router.push({ name: 'person-detail', params: { id: route.params.id } })
  }
}

const handleLogout = async () => {
  await authStore.logout()
  $q.notify({
    type: 'info',
    message: 'Logged out successfully',
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