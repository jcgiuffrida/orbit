<template>
  <q-layout view="lHh Lpr lFf">
    <AppHeader @toggle-drawer="leftDrawerOpen = !leftDrawerOpen" />

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
                    
                    <q-select
                      v-model="form.location"
                      label="Location"
                      hint="City or state"
                      filled
                      use-input
                      clearable
                      input-debounce="0"
                      new-value-mode="add-unique"
                      :options="locationOptions"
                      @filter="filterLocations"
                      class="q-mb-md"
                    >
                      <template v-slot:no-option>
                        <q-item>
                          <q-item-section class="text-grey">
                            Type to add new location
                          </q-item-section>
                        </q-item>
                      </template>
                    </q-select>
                    
                    <q-select
                      v-model="form.company"
                      label="Company"
                      filled
                      use-input
                      clearable
                      input-debounce="0"
                      new-value-mode="add-unique"
                      :options="companyOptions"
                      @filter="filterCompanies"
                      class="q-mb-md"
                    >
                      <template v-slot:no-option>
                        <q-item>
                          <q-item-section class="text-grey">
                            Type to add new company
                          </q-item-section>
                        </q-item>
                      </template>
                    </q-select>
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
                      v-model="form.address"
                      label="Address"
                      type="textarea"
                      filled
                      autocomplete="off"
                      class="q-mb-md"
                      rows="3"
                    />
                    
                    <!-- Birthday Fields -->
                    <div class="text-subtitle2 q-mb-sm">Birthday</div>
                    <div class="row q-gutter-md q-mb-md">
                      <div class="col">
                        <q-select
                          v-model="form.birthdayMonth"
                          :options="monthOptions"
                          label="Month"
                          filled
                          clearable
                          autocomplete="off"
                          option-value="value"
                          option-label="label"
                          emit-value
                          map-options
                        />
                      </div>
                      <div class="col-3">
                        <q-select
                          v-model="form.birthdayDay"
                          :options="dayOptions"
                          label="Day"
                          filled
                          clearable
                          autocomplete="off"
                          option-value="value"
                          option-label="label"
                          emit-value
                          map-options
                        />
                      </div>
                      <div class="col-3">
                        <q-input
                          v-model.number="form.birthYear"
                          label="Year"
                          type="number"
                          filled
                          clearable
                          autocomplete="off"
                          hint="Leave blank if unknown"
                          min="1900"
                          :max="new Date().getFullYear()"
                        />
                      </div>
                    </div>
                    
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
                    
                    <!-- <q-input
                      v-model="form.ai_summary"
                      label="AI Summary"
                      type="textarea"
                      rows="3"
                      filled
                      autocomplete="off"
                      class="q-mb-md"
                      hint="AI-generated summary of conversations and interactions"
                    /> -->
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
import { usePeopleStore } from '@/stores/people'
import AppHeader from '@/components/AppHeader.vue'
import NavigationDrawer from '@/components/NavigationDrawer.vue'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
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
  address: '',
  company: '',
  birthdayMonth: null,
  birthdayDay: null,
  birthYear: null,
  how_we_met: '',
  notes: '',
  ai_summary: ''
})

// Birthday options
const monthOptions = [
  { value: 1, label: 'January' },
  { value: 2, label: 'February' },
  { value: 3, label: 'March' },
  { value: 4, label: 'April' },
  { value: 5, label: 'May' },
  { value: 6, label: 'June' },
  { value: 7, label: 'July' },
  { value: 8, label: 'August' },
  { value: 9, label: 'September' },
  { value: 10, label: 'October' },
  { value: 11, label: 'November' },
  { value: 12, label: 'December' }
]

const dayOptions = Array.from({ length: 31 }, (_, i) => ({
  value: i + 1,
  label: (i + 1).toString()
}))

// Auto-complete data
const allLocationOptions = ref([])
const allCompanyOptions = ref([])
const locationOptions = ref([])
const companyOptions = ref([])

const resetForm = () => {
  form.name = ''
  form.name_ext = ''
  form.email = ''
  form.phone = ''
  form.location = ''
  form.address = ''
  form.company = ''
  form.birthdayMonth = null
  form.birthdayDay = null
  form.birthYear = null
  form.how_we_met = ''
  form.notes = ''
  form.ai_summary = ''
}

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
        // Map basic fields
        form.name = originalPerson.value.name || ''
        form.name_ext = originalPerson.value.name_ext || ''
        form.email = originalPerson.value.email || ''
        form.phone = originalPerson.value.phone || ''
        form.location = originalPerson.value.location || ''
        form.address = originalPerson.value.address || ''
        form.company = originalPerson.value.company || ''
        form.how_we_met = originalPerson.value.how_we_met || ''
        form.notes = originalPerson.value.notes || ''
        form.ai_summary = originalPerson.value.ai_summary || ''
        
        // Map birthday fields
        form.birthdayMonth = originalPerson.value.birthday_month || null
        form.birthdayDay = originalPerson.value.birthday_day || null
        form.birthYear = originalPerson.value.birth_year || null
      }
    } catch (error) {
      console.error('Failed to load person:', error)
    }
  }
}


const savePerson = async () => {
  isSaving.value = true
  
  try {
    // Prepare form data for backend
    const personData = {
      name: form.name,
      name_ext: form.name_ext,
      email: form.email,
      phone: form.phone,
      location: form.location === null ? '' : form.location,
      address: form.address,
      company: form.company === null ? '' : form.company,
      birthday_month: form.birthdayMonth,
      birthday_day: form.birthdayDay,
      birth_year: form.birthYear,
      how_we_met: form.how_we_met,
      notes: form.notes,
      ai_summary: form.ai_summary
    }
    
    if (isCreating.value) {
      // Create new person
      const newPerson = await peopleStore.createPerson(personData)
      
      $q.notify({
        type: 'positive',
        message: `Person ${newPerson.name} created successfully`,
        position: 'top',
        timeout: 6000,
        actions: [
          { 
            icon: 'add', 
            color: 'white', 
            dense: true, 
            label: 'Add Another',
            handler: () => {
              // Reset form to add another person
              resetForm()
              router.push({ name: 'person-edit', params: { id: 'new' } })
            }
          },
          { icon: 'close', color: 'white', dense: true }
        ]
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

// Auto-complete methods
const loadLocationSuggestions = async () => {
  try {
    const response = await fetch('/api/suggestions/locations/')
    const data = await response.json()
    allLocationOptions.value = data.locations || []
    locationOptions.value = [...allLocationOptions.value]
  } catch (error) {
    console.error('Failed to load location suggestions:', error)
  }
}

const loadCompanySuggestions = async () => {
  try {
    const response = await fetch('/api/suggestions/companies/')
    const data = await response.json()
    allCompanyOptions.value = data.companies || []
    companyOptions.value = [...allCompanyOptions.value]
  } catch (error) {
    console.error('Failed to load company suggestions:', error)
  }
}

const filterLocations = (val, update) => {
  update(() => {
    if (val === '') {
      locationOptions.value = [...allLocationOptions.value]
    } else {
      const needle = val.toLowerCase()
      locationOptions.value = allLocationOptions.value.filter(v => 
        v.toLowerCase().indexOf(needle) > -1
      )
    }
  })
}

const filterCompanies = (val, update) => {
  update(() => {
    if (val === '') {
      companyOptions.value = [...allCompanyOptions.value]
    } else {
      const needle = val.toLowerCase()
      companyOptions.value = allCompanyOptions.value.filter(v => 
        v.toLowerCase().indexOf(needle) > -1
      )
    }
  })
}


// Lifecycle
onMounted(() => {
  loadPerson()
  loadLocationSuggestions()
  loadCompanySuggestions()
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