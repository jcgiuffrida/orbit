<template>
  <q-layout view="lHh Lpr lFf">
    <AppHeader @toggle-drawer="leftDrawerOpen = !leftDrawerOpen" />

    <NavigationDrawer v-model="leftDrawerOpen" />

    <q-page-container>
      <q-page class="q-pa-md">
        <div v-if="loading" class="flex flex-center q-mt-lg">
          <q-spinner size="2em" />
        </div>
        
        <div v-else-if="error" class="text-center q-mt-lg">
          <q-icon name="error" size="2em" color="negative" />
          <div class="text-h6 q-mt-md">Failed to load dashboard</div>
          <div class="text-body2">{{ error }}</div>
          <q-btn @click="loadDashboard" color="primary" class="q-mt-md">Retry</q-btn>
        </div>

        <div v-else>
          <!-- Page Header with Actions -->
          <div class="row items-center q-mb-lg">
            <div class="col">
              <h1 class="text-h4 q-ma-none">Dashboard</h1>
            </div>
            <div class="col-auto">
              <div class="q-gutter-sm">
                <q-btn 
                  color="accent"
                  icon="add_comment" 
                  :to="{ name: 'conversation-create' }"
                  :label="$q.screen.gt.xs ? 'New Conversation' : undefined"
                >
                  <q-tooltip v-if="!$q.screen.gt.xs">New Conversation</q-tooltip>
                </q-btn>
                <q-btn 
                  color="secondary"
                  icon="contact_phone" 
                  :to="{ name: 'ping-create' }"
                  :label="$q.screen.gt.xs ? 'New Ping' : undefined"
                >
                  <q-tooltip v-if="!$q.screen.gt.xs">New Ping</q-tooltip>
                </q-btn>
                <q-btn 
                  color="primary"
                  icon="person_add" 
                  :to="{ name: 'person-edit', params: {id: 'new' } }"
                  :label="$q.screen.gt.xs ? 'Add Person' : undefined"
                >
                  <q-tooltip v-if="!$q.screen.gt.xs">Add Person</q-tooltip>
                </q-btn>
              </div>
            </div>
          </div>
          
          <!-- Monthly Activity Chart -->
          <div class="row q-mb-lg">
            <div class="col-12">
              <q-card>
                <q-card-section>
                  <div class="text-h6">Activity Over Past Year</div>
                </q-card-section>
                <q-card-section>
                  <ActivityChart :data="dashboardData.monthly_activity" />
                </q-card-section>
              </q-card>
            </div>
          </div>

          <!-- Activity Overview -->
          <div class="row q-mb-lg">
            <div class="col-12">
              <q-card>
                <q-card-section>
                  <div class="text-h6">Conversations Overview</div>
                </q-card-section>
                <q-card-section>
                  <div class="row q-col-gutter-md">
                    <div class="col">
                      <div class="text-caption">Past Week</div>
                      <div class="text-h6">{{ dashboardData.activity_overview.conversations.week }} <span class="gt-sm">conversations</span></div>
                      <div v-if="dashboardData.activity_overview.contact_attempts.week > 0" class="text-body2">+ {{ dashboardData.activity_overview.contact_attempts.week }} pings</div>
                    </div>
                    <div class="col">
                      <div class="text-caption">Past Month</div>
                      <div class="text-h6">{{ dashboardData.activity_overview.conversations.month }} <span class="gt-sm">conversations</span></div>
                      <div v-if="dashboardData.activity_overview.contact_attempts.month > 0" class="text-body2">+ {{ dashboardData.activity_overview.contact_attempts.month }} pings</div>
                    </div>
                    <div class="col">
                      <div class="text-caption">Past Year</div>
                      <div class="text-h6">{{ dashboardData.activity_overview.conversations.year }} <span class="gt-sm">conversations</span></div>
                      <div v-if="dashboardData.activity_overview.contact_attempts.year > 0" class="text-body2">+ {{ dashboardData.activity_overview.contact_attempts.year }} pings</div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <!-- Recent Conversations and Top Contacts -->
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-12 col-md-6">
              <q-card>
                <q-card-section>
                  <div class="text-h6">Recent Conversations</div>
                </q-card-section>
                <q-card-section>
                  <q-list separator>
                    <q-item 
                      v-for="conversation in dashboardData.recent_conversations.slice(0, 8)" 
                      :key="conversation.id"
                      :to="{ name: 'conversation-detail', params: { id: conversation.id } }"
                      clickable
                    >
                      <q-item-section>
                        <q-item-label>{{ formatDate(conversation.date) }}</q-item-label>
                        <q-item-label caption>
                          {{ conversation.participants.map(p => p.name).join(', ') }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
                <q-card-actions align="center">
                  <q-btn flat :to="{ name: 'conversations' }">View all</q-btn>
                </q-card-actions>
              </q-card>
            </div>
            
            <div class="col-12 col-md-6">
              <q-card>
                <q-card-section>
                  <div class="text-h6">Top Contacts</div>
                  <div class="text-subtitle2">Past two years</div>
                </q-card-section>
                <q-card-section>
                  <q-list separator>
                    <q-item 
                      v-for="person in dashboardData.top_contacts.slice(0, 8)" 
                      :key="person.id"
                      :to="{ name: 'person-detail', params: { id: person.id } }"
                      clickable
                    >
                      <q-item-section>
                        <q-item-label>{{ person.name }}</q-item-label>
                        <q-item-label caption>
                          {{ person.conversation_count_recent }} {{ pluralize(person.conversation_count_recent, 'conversation', 'conversations') }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
                <q-card-actions align="center">
                  <q-btn flat :to="{ name: 'people' }">View all</q-btn>
                </q-card-actions>
              </q-card>
            </div>
          </div>

          <!-- Upcoming Birthdays -->
          <div class="row q-mb-lg" v-if="dashboardData.upcoming_birthdays && dashboardData.upcoming_birthdays.length > 0">
            <div class="col-12">
              <q-card>
                <q-card-section>
                  <div class="row items-center">
                    <div class="col">
                      <div class="text-h6">
                        Upcoming Birthdays
                      </div>
                    </div>
                    <div class="col-auto">
                      <q-btn flat dense :to="{ name: 'birthdays' }" color="primary">
                        View Calendar
                        <q-icon name="chevron_right" />
                      </q-btn>
                    </div>
                  </div>
                </q-card-section>
                <q-card-section>
                  <div class="row q-col-gutter-md">
                    <div 
                      v-for="birthday in dashboardData.upcoming_birthdays.slice(0, 6)" 
                      :key="birthday.id"
                      class="col-12 col-sm-6 col-md-4 col-lg-3"
                    >
                      <div 
                        class="birthday-item q-pa-sm rounded-borders cursor-pointer"
                        :class="{ 'bg-accent text-white': birthday.is_today, 'bg-grey-3': !birthday.is_today }"
                        @click="goToPerson(birthday.id)"
                      >
                        <div class="row items-center q-gutter-sm">
                          <div class="col-auto">
                            <q-icon 
                              :name="birthday.is_today ? 'celebration' : 'cake'" 
                              size="24px"
                              :color="birthday.is_today ? 'white' : 'primary'"
                            />
                          </div>
                          <div class="col">
                            <div :class="birthday.is_today ? 'text-white' : 'text-body1'" class="text-weight-medium">
                              {{ birthday.name }}
                            </div>
                            <div :class="birthday.is_today ? 'text-white' : 'text-caption text-grey-6'">
                              <span v-if="birthday.is_today" class="text-weight-bold">Today!</span>
                              <span v-else-if="birthday.days_until === 1">Tomorrow</span>
                              <span v-else>{{ birthday.days_until }} days</span>
                              <span v-if="birthday.age" class="q-ml-sm">({{ birthday.age }})</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <!-- People to Reach Out -->
          <div class="row">
            <div class="col-12">
              <q-card>
                <q-card-section>
                  <div class="text-h6">People to Reach Out</div>
                </q-card-section>
                <q-card-section v-if="dashboardData.people_to_reach_out.length === 0">
                  <div class="text-body2 text-grey-6">Great! You're up to date with everyone.</div>
                </q-card-section>
                <q-card-section v-else>
                  <div class="row q-col-gutter-md">
                    <div 
                      v-for="person in dashboardData.people_to_reach_out" 
                      :key="person.id"
                      class="col-12 col-sm-6 col-md-4"
                    >
                      <q-card class="cursor-pointer" @click="$router.push({ name: 'person-detail', params: { id: person.id } })">
                        <q-card-section>
                          <div class="text-h6">{{ person.name }}</div>
                          <div class="text-caption text-grey-6" v-if="person.days_since_last_contact">
                            {{ person.days_since_last_contact }} days ago
                          </div>
                        </q-card-section>
                      </q-card>
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
import { useQuasar } from 'quasar'
import api from '@/services/api'
import AppHeader from '@/components/AppHeader.vue'
import NavigationDrawer from '@/components/NavigationDrawer.vue'
import ActivityChart from '@/components/ActivityChart.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const $q = useQuasar()

const leftDrawerOpen = ref(false)
const dashboardData = ref({})
const loading = ref(true)
const error = ref(null)

const loadDashboard = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await api.get('/dashboard/')
    dashboardData.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load dashboard data'
    console.error('Dashboard load error:', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    weekday: 'short',
    month: 'short', 
    day: 'numeric'
  })
}

const pluralize = (count, singular, plural) => {
  return count === 1 ? singular : plural
}

const goToPerson = (personId) => {
  router.push({ name: 'person-detail', params: { id: personId } })
}

onMounted(() => {
  loadDashboard()
})
</script>