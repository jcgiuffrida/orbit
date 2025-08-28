import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const loading = ref(false)
  const initialized = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!user.value)
  const isLoading = computed(() => loading.value)

  // Actions
  const checkAuth = async () => {
    loading.value = true
    try {
      const userData = await authService.getCurrentUser()
      user.value = userData
      initialized.value = true
    } catch (error) {
      console.error('Auth check failed:', error)
      user.value = null
      initialized.value = true
    } finally {
      loading.value = false
    }
  }

  const login = async (username, password) => {
    loading.value = true
    try {
      const response = await authService.login(username, password)
      if (response.success) {
        user.value = response.user
        return { success: true }
      } else {
        return { success: false, error: response.error || 'Login failed' }
      }
    } catch (error) {
      console.error('Login failed:', error)
      const message = error.response?.data?.error || 'Login failed'
      return { success: false, error: message }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    loading.value = true
    try {
      await authService.logout()
      user.value = null
    } catch (error) {
      console.error('Logout failed:', error)
      // Clear user anyway
      user.value = null
    } finally {
      loading.value = false
    }
  }

  const clearAuth = () => {
    user.value = null
    initialized.value = false
  }

  return {
    // State
    user,
    loading,
    initialized,
    
    // Getters
    isAuthenticated,
    isLoading,
    
    // Actions
    checkAuth,
    login,
    logout,
    clearAuth
  }
})