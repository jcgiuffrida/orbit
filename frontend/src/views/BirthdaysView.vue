<template>
  <q-layout view="lHh Lpr lFf">
    <AppHeader @toggle-drawer="leftDrawerOpen = !leftDrawerOpen" />

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="q-pa-md" style="background-color: #f8f9fa;">
        <!-- Loading State -->
        <div v-if="loading" class="flex flex-center q-mt-lg">
          <q-spinner size="2em" />
        </div>
        
        <!-- Error State -->
        <div v-else-if="error" class="text-center q-mt-lg">
          <q-icon name="error" size="2em" color="negative" />
          <div class="text-h6 q-mt-md">Failed to load birthdays</div>
          <div class="text-body2">{{ error }}</div>
          <q-btn @click="loadBirthdays" color="primary" class="q-mt-md">Retry</q-btn>
        </div>

        <div v-else>
          <!-- Page Header -->
          <div class="row items-center q-mb-lg">
            <div class="col">
              <h1 class="text-h4 q-ma-none">
                Birthday Calendar
              </h1>
              <p class="text-subtitle1 text-grey-6 q-ma-none q-mt-sm">
                Upcoming birthdays starting today
              </p>
            </div>
          </div>

          <!-- No Birthdays Message -->
          <div v-if="!birthdayData || birthdayData.birthdays.length === 0" class="text-center q-mt-xl">
            <q-icon name="cake" size="80px" color="grey-5" />
            <div class="text-h6 q-mt-md text-grey-7">No upcoming birthdays</div>
            <div class="text-body2 text-grey-6">
              Add birthday information to people's profiles to see them here
            </div>
            <q-btn 
              color="primary" 
              :to="{ name: 'people' }" 
              class="q-mt-md"
              label="View People"
            />
          </div>

          <!-- Birthday Timeline -->
          <div v-else class="row q-col-gutter-md">
            <div class="col-12">
              <q-card>
                <q-card-section>
                  <div class="text-h6 q-mb-md">Next {{ birthdayData.birthdays.length }} Birthdays</div>
                  
                  <!-- Birthday List -->
                  <div class="birthday-timeline">
                    <div 
                      v-for="(birthday, index) in birthdayData.birthdays" 
                      :key="birthday.id"
                      class="birthday-entry q-mb-md"
                      :class="{ 'birthday-today': birthday.is_today }"
                    >
                      <div class="row items-center q-gutter-md">
                        <!-- Date Column -->
                        <div class="col-auto birthday-date-col">
                          <div 
                            class="birthday-date-badge q-pa-md text-center"
                            :class="{ 
                              'bg-accent text-white': birthday.is_today,
                              'bg-primary text-white': birthday.days_until <= 7 && !birthday.is_today,
                              'bg-grey-2': birthday.days_until > 7
                            }"
                          >
                            <div v-if="birthday.is_today" class="text-h6 text-weight-bold">TODAY</div>
                            <div v-else-if="birthday.days_until === 1" class="text-subtitle1 text-weight-bold">TOMORROW</div>
                            <div v-else-if="birthday.days_until <= 7" class="text-subtitle1 text-weight-bold">
                              {{ birthday.days_until }} DAYS
                            </div>
                            <div v-else class="text-body2">
                              {{ formatBirthdayDate(birthday.next_birthday) }}
                            </div>
                          </div>
                        </div>

                        <!-- Person Info -->
                        <div class="col">
                          <q-card 
                            flat
                            class="cursor-pointer birthday-person-card"
                            :class="{ 'bg-accent-1': birthday.is_today }"
                            @click="goToPerson(birthday.id)"
                          >
                            <q-card-section class="q-pa-md">
                              <div class="row items-center q-gutter-md">
                                <div class="col-auto">
                                  <q-icon 
                                    :name="birthday.is_today ? 'celebration' : 'cake'" 
                                    size="32px"
                                    :color="birthday.is_today ? 'accent' : 'primary'"
                                  />
                                </div>
                                <div class="col">
                                  <div class="text-h6">{{ birthday.name }}</div>
                                  <div class="text-subtitle2 text-grey-6">
                                    {{ birthday.birthday_display }}
                                    <span v-if="birthday.age" class="q-ml-sm">(turning {{ birthday.age }})</span>
                                  </div>
                                  <div v-if="birthday.name_ext" class="text-caption text-grey-6">
                                    {{ birthday.name_ext }}
                                  </div>
                                </div>
                                <div class="col-auto">
                                  <q-btn 
                                    flat 
                                    dense 
                                    round 
                                    icon="contact_phone" 
                                    color="grey-6"
                                    @click.stop="createPing(birthday.id)"
                                  >
                                    <q-tooltip>Log Birthday Ping</q-tooltip>
                                  </q-btn>
                                </div>
                              </div>
                            </q-card-section>
                          </q-card>
                        </div>
                      </div>

                      <!-- Divider -->
                      <q-separator 
                        v-if="index < birthdayData.birthdays.length - 1" 
                        class="q-mt-md" 
                        color="grey-3"
                      />
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import NavigationDrawer from '@/components/NavigationDrawer.vue'

const router = useRouter()
const leftDrawerOpen = ref(false)
const loading = ref(true)
const error = ref(null)
const birthdayData = ref(null)

const loadBirthdays = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await fetch('/api/birthdays/', {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    birthdayData.value = await response.json()
  } catch (err) {
    console.error('Failed to load birthdays:', err)
    error.value = 'Unable to load birthdays. Please try again.'
  } finally {
    loading.value = false
  }
}

const goToPerson = (personId) => {
  router.push({ name: 'person-detail', params: { id: personId } })
}

const createPing = (personId) => {
  router.push({ 
    name: 'ping-create', 
    query: { person: personId } 
  })
}

const formatBirthdayDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, { 
    month: 'short', 
    day: 'numeric'
  })
}

onMounted(() => {
  loadBirthdays()
})
</script>

<style scoped>
.birthday-date-col {
  min-width: 120px;
}

.birthday-date-badge {
  border-radius: 8px;
  min-height: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
}

.birthday-person-card {
  transition: all 0.2s ease;
}

.birthday-person-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  transform: translateY(-1px);
}

.birthday-today .birthday-person-card {
  border-left: 4px solid var(--q-accent);
}

.birthday-timeline {
  max-width: 100%;
}

.birthday-entry {
  position: relative;
}

@media (max-width: 599px) {
  .birthday-date-col {
    min-width: 80px;
  }
  
  .birthday-date-badge {
    min-height: 50px;
    font-size: 0.8em;
  }
}
</style>