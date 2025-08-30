<template>
  <q-card class="content-card" flat bordered>
    <q-card-section class="q-pa-lg">
      <div class="row items-center q-mb-md">
        <div class="text-h6 text-weight-medium col">Relationships</div>
        <q-btn 
          outline
          color="primary" 
          icon="add" 
          label="Add Relationship"
          size="sm"
          @click="openAddDialog"
        />
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center q-pa-md">
        <q-spinner-dots size="30px" color="primary" />
        <div class="q-mt-sm text-grey-6">Loading relationships...</div>
      </div>

      <!-- Empty State -->
      <div v-else-if="relationships.length === 0" class="text-center q-pa-lg">
        <q-icon name="people_outline" size="48px" color="grey-5" />
        <div class="text-body2 text-grey-6 q-mt-sm">No relationships recorded</div>
        <q-btn 
          outline
          color="primary" 
          icon="add" 
          label="Add First Relationship"
          size="sm"
          class="q-mt-md"
          @click="openAddDialog"
        />
      </div>

      <!-- Relationships List -->
      <div v-else>
        <div 
          v-for="relationship in relationships" 
          :key="relationship.id"
          class="relationship-item q-mb-md"
        >
          <div class="row items-center q-gutter-sm">
            <!-- Relationship Icon -->
            <q-icon 
              :name="getRelationshipIcon(relationship.relationship_type)" 
              size="20px" 
              color="grey-7" 
            />
            
            <!-- Relationship Info -->
            <div class="col">
              <div class="text-body1">
                <router-link :to="{ name: 'person-detail', params: { id: getOtherPersonName(relationship) === relationship.person1_name ? relationship.person1 : relationship.person2 } }">
                  {{ getOtherPersonName(relationship) }}
                </router-link>
              </div>
              <div class="text-caption text-grey-6">
                {{ getRelationshipTypeLabel(relationship.relationship_type) }}
                <span v-if="relationship.description">
                  • {{ relationship.description }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="row q-gutter-xs">
              <q-btn 
                flat
                dense
                round
                size="sm"
                icon="edit"
                color="grey-6"
                @click="editRelationship(relationship)"
              >
                <q-tooltip>Edit</q-tooltip>
              </q-btn>
              <q-btn 
                flat
                dense
                round
                size="sm"
                icon="delete"
                color="grey-6"
                @click="confirmDeleteRelationship(relationship)"
              >
                <q-tooltip>Delete</q-tooltip>
              </q-btn>
            </div>
          </div>
        </div>
      </div>
    </q-card-section>

    <!-- Add/Edit Relationship Dialog -->
    <q-dialog v-model="showAddDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">
            {{ editingRelationship ? 'Edit Relationship' : 'Add Relationship' }}
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="q-gutter-md">
            <!-- Person Selection -->
            <q-select
              v-model="form.selectedPerson"
              :options="peopleOptions"
              option-label="name"
              option-value="id"
              label="Person *"
              filled
              use-input
              hide-selected
              fill-input
              input-debounce="300"
              clearable
              autofocus
              emit-value
              map-options
              @filter="filterPeople"
              @popup-show="ensurePeopleLoaded"
              :rules="[val => !!val || 'Person is required']"
            >
              <template v-slot:no-option>
                <q-item>
                  <q-item-section class="text-grey">
                    {{ peopleOptions.length === 0 ? 'Loading people...' : 'No people found' }}
                  </q-item-section>
                </q-item>
              </template>
            </q-select>

            <!-- Relationship Type -->
            <q-select
              v-model="form.relationshipType"
              :options="relationshipTypeOptions"
              label="Relationship Type *"
              filled
              emit-value
              map-options
              :rules="[val => !!val || 'Relationship type is required']"
            />

            <!-- Description -->
            <q-input
              v-model="form.description"
              label="Description"
              hint="e.g., 'college roommate', 'sister-in-law'"
              filled
              autocomplete="off"
            />
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="grey-7" @click="cancelEdit" />
          <q-btn 
            flat 
            :label="editingRelationship ? 'Save Changes' : 'Add Relationship'"
            color="primary" 
            :loading="saving"
            @click="saveRelationship"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Delete Confirmation Dialog -->
    <q-dialog v-model="showDeleteDialog">
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="warning" color="negative" text-color="white" />
          <span class="q-ml-sm">
            Are you sure you want to delete the relationship with 
            <strong>{{ relationshipToDelete?.person1_name === personName ? relationshipToDelete?.person2_name : relationshipToDelete?.person1_name }}</strong>?
          </span>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="primary" @click="showDeleteDialog = false" />
          <q-btn flat label="Delete" color="negative" @click="deleteRelationship" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-card>
</template>

<script setup>
import { ref, onMounted, computed, reactive, watch } from 'vue'
import { useQuasar } from 'quasar'
import relationshipsService from '@/services/relationships'
import { usePeopleStore } from '@/stores/people'

const props = defineProps({
  personId: {
    type: String,
    required: true
  },
  personName: {
    type: String,
    required: true
  }
})

const $q = useQuasar()
const peopleStore = usePeopleStore()

// State
const relationships = ref([])
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showDeleteDialog = ref(false)
const editingRelationship = ref(null)
const relationshipToDelete = ref(null)
const peopleOptions = ref([])

// Form data
const form = reactive({
  selectedPerson: null,
  relationshipType: '',
  description: ''
})

// Computed
const relationshipTypeOptions = computed(() => relationshipsService.getRelationshipTypes())

// Methods
const loadRelationships = async () => {
  loading.value = true
  try {
    relationships.value = await relationshipsService.getByPerson(props.personId)
  } catch (error) {
    console.error('Error loading relationships:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to load relationships',
      position: 'top',
      timeout: 3000
    })
  } finally {
    loading.value = false
  }
}

const loadPeopleOptions = async () => {
  try {
    // Force refresh if we only have 1 person (likely from direct detail page navigation)
    const shouldForceRefresh = peopleStore.peopleCount <= 1
    await peopleStore.fetchPeople(shouldForceRefresh)
    
    // Exclude the current person from options
    const allPeople = peopleStore.getPeopleList
    peopleOptions.value = allPeople.filter(person => person.id !== props.personId)
  } catch (error) {
    console.error('Error loading people:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to load people list',
      position: 'top',
      timeout: 3000
    })
  }
}

const filterPeople = (val, update) => {
  update(() => {
    const allPeople = peopleStore.getPeopleList
    
    if (val === '') {
      peopleOptions.value = allPeople.filter(person => person.id !== props.personId)
    } else {
      const needle = val.toLowerCase()
      peopleOptions.value = allPeople.filter(person => 
        person.id !== props.personId && person.name.toLowerCase().includes(needle)
      )
    }
  })
}

const getOtherPersonName = (relationship) => {
  return relationship.person1 === props.personId ? 
    relationship.person2_name : 
    relationship.person1_name
}

const getRelationshipTypeLabel = (type) => {
  const option = relationshipTypeOptions.value.find(opt => opt.value === type)
  return option ? option.label : type
}

const getRelationshipIcon = (type) => {
  const icons = {
    partner: 'favorite',
    family: 'family_restroom',
    friend: 'people',
    colleague: 'work',
    acquaintance: 'person',
    other: 'help'
  }
  return icons[type] || 'person'
}

const editRelationship = (relationship) => {
  editingRelationship.value = relationship
  form.selectedPerson = relationship.person1 === props.personId ? relationship.person2 : relationship.person1
  form.relationshipType = relationship.relationship_type
  form.description = relationship.description || ''
  showAddDialog.value = true
}

const confirmDeleteRelationship = (relationship) => {
  relationshipToDelete.value = relationship
  showDeleteDialog.value = true
}

const saveRelationship = async () => {
  if (!form.selectedPerson || !form.relationshipType) {
    $q.notify({
      type: 'warning',
      message: 'Please fill in all required fields',
      position: 'top',
      timeout: 3000
    })
    return
  }

  saving.value = true
  try {
    const relationshipData = {
      person1: props.personId,
      person2: form.selectedPerson,
      relationship_type: form.relationshipType,
      description: form.description || ''
    }

    if (editingRelationship.value) {
      await relationshipsService.update(editingRelationship.value.id, relationshipData)
      $q.notify({
        type: 'positive',
        message: 'Relationship updated successfully',
        position: 'top',
        timeout: 3000
      })
    } else {
      await relationshipsService.create(relationshipData)
      $q.notify({
        type: 'positive',
        message: 'Relationship added successfully',
        position: 'top',
        timeout: 3000
      })
    }

    await loadRelationships()
    cancelEdit()
  } catch (error) {
    console.error('Error saving relationship:', error)
    $q.notify({
      type: 'negative',
      message: `Failed to ${editingRelationship.value ? 'update' : 'add'} relationship`,
      position: 'top',
      timeout: 3000
    })
  } finally {
    saving.value = false
  }
}

const deleteRelationship = async () => {
  if (!relationshipToDelete.value) return

  try {
    await relationshipsService.delete(relationshipToDelete.value.id)
    $q.notify({
      type: 'positive',
      message: 'Relationship deleted successfully',
      position: 'top',
      timeout: 3000
    })
    
    await loadRelationships()
    showDeleteDialog.value = false
    relationshipToDelete.value = null
  } catch (error) {
    console.error('Error deleting relationship:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to delete relationship',
      position: 'top',
      timeout: 3000
    })
  }
}

const openAddDialog = async () => {
  await ensurePeopleLoaded()
  showAddDialog.value = true
}

const ensurePeopleLoaded = async () => {
  // Always refresh if we have less than 2 people (current person + at least 1 other)
  if (peopleOptions.value.length < 1) {
    await loadPeopleOptions()
  }
}

const cancelEdit = () => {
  showAddDialog.value = false
  editingRelationship.value = null
  form.selectedPerson = null
  form.relationshipType = ''
  form.description = ''
}

// Watch for personId changes and reload relationships
watch(() => props.personId, (newPersonId, oldPersonId) => {
  if (newPersonId && newPersonId !== oldPersonId) {
    loadRelationships()
  }
}, { immediate: false })

// Lifecycle
onMounted(() => {
  loadRelationships()
  loadPeopleOptions()
})
</script>

<style scoped>
.relationship-item {
  padding: 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.relationship-item:last-child {
  border-bottom: none;
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
</style>