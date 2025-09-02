import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue')
    },
    {
      path: '/people',
      name: 'people',
      component: () => import('@/views/PeopleView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/people/:id',
      name: 'person-detail',
      component: () => import('@/views/PersonDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/people/:id/edit',
      name: 'person-edit',
      component: () => import('@/views/PersonEditView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/conversations',
      name: 'conversations', 
      component: () => import('@/views/ConversationsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/conversations/new',
      name: 'conversation-create',
      component: () => import('@/views/ConversationCreateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/conversations/:id',
      name: 'conversation-detail',
      component: () => import('@/views/ConversationDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/conversations/:id/edit',
      name: 'conversation-edit',
      component: () => import('@/views/ConversationCreateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/pings',
      name: 'pings',
      component: () => import('@/views/ContactAttemptsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/pings/new',
      name: 'ping-create',
      component: () => import('@/views/ContactAttemptCreateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/pings/:id/edit',
      name: 'ping-edit',
      component: () => import('@/views/ContactAttemptCreateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/birthdays',
      name: 'birthdays',
      component: () => import('@/views/BirthdaysView.vue'),
      meta: { requiresAuth: true }
    },
  ]
})

// Navigation guard for authentication
router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  
  // Check if we need to initialize auth state
  if (!authStore.initialized) {
    await authStore.checkAuth()
  }
  
  // If route requires auth and user is not authenticated, redirect to login
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'login' }
  }
  
  // If user is authenticated and tries to access login, redirect to home
  if (to.name === 'login' && authStore.isAuthenticated) {
    return { name: 'home' }
  }
})

export default router