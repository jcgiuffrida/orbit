<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat round dense icon="menu" @click="leftDrawerOpen = !leftDrawerOpen" />
        <q-toolbar-title>People</q-toolbar-title>
        <q-space />
        <q-btn flat round dense icon="logout" @click="handleLogout" />
      </q-toolbar>
    </q-header>

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="q-pa-md">
        <!-- Header -->
        <div class="row items-center q-mb-lg">
          <div class="text-h4 col">People</div>
          <q-btn 
            color="primary" 
            icon="add" 
            label="Add Person" 
            @click="showAddDialog = true" 
          />
        </div>

        <!-- Search and Sorting -->
        <div class="row q-col-gutter-md q-mb-lg">
          <div class="col-12 col-md-8">
            <q-input
              v-model="searchQuery"
              filled
              placeholder="Search people..."
              clearable
            >
              <template v-slot:prepend>
                <q-icon name="search" />
              </template>
            </q-input>
          </div>
          <div class="col-12 col-md-4">
            <q-select
              v-model="sortBy"
              filled
              :options="sortOptions"
              label="Sort by"
              emit-value
              map-options
              @update:model-value="loadPeople"
            />
          </div>
        </div>

        <!-- People Grid -->
        <div v-if="loading" class="text-center q-pa-lg">
          <q-spinner-dots size="50px" color="primary" />
          <div class="q-mt-md">Loading people...</div>
        </div>

        <div v-else-if="filteredPeople.length === 0" class="text-center q-pa-xl">
          <q-icon name="people_outline" size="80px" color="grey-5" />
          <div class="text-h6 text-grey-7 q-mt-md">
            {{ searchQuery ? 'No people found matching your search' : 'No people added yet' }}
          </div>
          <q-btn 
            v-if="!searchQuery"
            color="primary" 
            label="Add Your First Person" 
            class="q-mt-md"
            @click="showAddDialog = true"
          />
        </div>

        <div v-else class="row q-col-gutter-md">
          <div 
            v-for="person in filteredPeople" 
            :key="person.id"
            class="col-12 col-sm-6 col-md-4 col-lg-3"
          >
            <q-card class="person-card full-height cursor-pointer" @click="viewPerson(person)">
              <q-card-section>
                <div class="text-h6 q-mb-xs">{{ person.name }}</div>
                <div v-if="person.name_ext" class="text-caption text-grey-7 q-mb-sm">
                  {{ person.name_ext }}
                </div>
                <div v-if="person.location" class="text-body2 text-grey-8 q-mb-sm">
                  <q-icon name="place" size="16px" class="q-mr-xs" />
                  {{ person.location }}
                </div>
                <div v-if="person.last_contacted" class="text-caption text-accent">
                  <q-icon name="schedule" size="14px" class="q-mr-xs" />
                  Last contact: {{ formatDate(person.last_contacted) }}
                </div>
                <div v-else class="text-caption text-grey-6">
                  <q-icon name="schedule" size="14px" class="q-mr-xs" />
                  No contact recorded
                </div>
              </q-card-section>

              <q-card-actions align="right">
                <q-btn 
                  v-if="person.email"
                  flat 
                  round 
                  size="md" 
                  icon="email" 
                  color="info"
                  @click.stop="copyEmail(person)"
                >
                  <q-tooltip>Copy Email Address</q-tooltip>
                </q-btn>
                <q-btn 
                  v-if="person.phone"
                  flat 
                  round 
                  size="md" 
                  icon="sms" 
                  color="info"
                  @click.stop="textPerson(person)"
                >
                  <q-tooltip>Send Text Message</q-tooltip>
                </q-btn>
                <q-btn 
                  flat 
                  round 
                  size="md" 
                  icon="add" 
                  color="primary"
                  @click.stop="addConversation(person)"
                >
                  <q-tooltip>Log Conversation</q-tooltip>
                </q-btn>
              </q-card-actions>
            </q-card>
          </div>
        </div>

        <!-- Add Person Dialog -->
        <q-dialog v-model="showAddDialog" persistent>
          <q-card style="min-width: 400px">
            <q-card-section>
              <div class="text-h6">Add New Person</div>
            </q-card-section>
            <q-card-section class="q-pt-none">
              <div class="text-body2">Coming soon...</div>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancel" color="primary" @click="showAddDialog = false" />
            </q-card-actions>
          </q-card>
        </q-dialog>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NavigationDrawer from '@/components/NavigationDrawer.vue'
import peopleService from '@/services/people'

export default {
  name: 'PeopleView',
  components: {
    NavigationDrawer
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const leftDrawerOpen = ref(false)

    // Data
    const people = ref([])
    const loading = ref(true)
    const searchQuery = ref('')
    const sortBy = ref('name')
    const showAddDialog = ref(false)

    // Options for sorting
    const sortOptions = [
      { label: 'Name (A-Z)', value: 'name' },
      { label: 'Name (Z-A)', value: '-name' },
      { label: 'Recently Contacted', value: '-last_contacted' },
      { label: 'Least Recently Contacted', value: 'last_contacted' }
    ]

    // Computed
    const filteredPeople = computed(() => {
      let filtered = [...people.value]

      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase().trim()
        filtered = filtered.filter(person => 
          person.name.toLowerCase().includes(query) ||
          (person.name_ext && person.name_ext.toLowerCase().includes(query)) ||
          (person.location && person.location.toLowerCase().includes(query))
        )
      }


      // Apply sorting
      filtered.sort((a, b) => {
        switch (sortBy.value) {
          case 'name':
            return a.name.localeCompare(b.name)
          case '-name':
            return b.name.localeCompare(a.name)
          case '-last_contacted':
            if (!a.last_contacted && !b.last_contacted) return 0
            if (!a.last_contacted) return 1
            if (!b.last_contacted) return -1
            return new Date(b.last_contacted) - new Date(a.last_contacted)
          case 'last_contacted':
            if (!a.last_contacted && !b.last_contacted) return 0
            if (!a.last_contacted) return 1
            if (!b.last_contacted) return -1
            return new Date(a.last_contacted) - new Date(b.last_contacted)
          default:
            return 0
        }
      })

      return filtered
    })

    // Methods
    const loadPeople = async () => {
      loading.value = true
      try {
        const response = await peopleService.getAll()
        people.value = response.results || response
      } catch (error) {
        console.error('Error loading people:', error)
        people.value = []
      } finally {
        loading.value = false
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

    const copyEmail = async (person) => {
      if (!person.email) {
        // TODO: Show notification that no email is available
        console.log('No email address for', person.name)
        return
      }
      
      try {
        await navigator.clipboard.writeText(person.email)
        // TODO: Show success notification
        console.log('Email copied:', person.email)
      } catch (error) {
        console.error('Failed to copy email:', error)
        // TODO: Show error notification
      }
    }

    const viewPerson = (person) => {
      // TODO: Navigate to person detail view
      console.log('View person:', person)
    }


    const textPerson = (person) => {
      if (person.phone) {
        window.open(`sms:${person.phone}`)
      } else {
        // TODO: Show notification that no phone number is available
        console.log('No phone number for', person.name)
      }
    }

    const addConversation = (person) => {
      // TODO: Navigate to add conversation with person pre-selected
      console.log('Add conversation with:', person)
    }

    const handleLogout = async () => {
      await authStore.logout()
      router.push({ name: 'login' })
    }

    // Lifecycle
    onMounted(() => {
      loadPeople()
    })

    return {
      leftDrawerOpen,
      authStore,
      handleLogout,
      people,
      loading,
      searchQuery,
      sortBy,
      showAddDialog,
      sortOptions,
      filteredPeople,
      loadPeople,
      formatDate,
      viewPerson,
      copyEmail,
      textPerson,
      addConversation
    }
  }
}
</script>

<style scoped>
.person-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid rgba(0,0,0,0.12);
}

.person-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.person-card .q-card__section {
  padding: 16px;
}

.person-card .q-card__actions {
  padding: 12px 16px 16px 16px;
  background: rgba(0,0,0,0.02);
}

.person-card .q-card__actions .q-btn {
  min-width: 40px;
  min-height: 40px;
}
</style>