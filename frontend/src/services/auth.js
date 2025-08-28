import api from './api'

export const authService = {
  // Check current authentication status
  async getCurrentUser() {
    try {
      const response = await api.get('auth/user/')
      return response.data
    } catch (error) {
      if (error.response?.status === 403) {
        return null // Not authenticated
      }
      throw error
    }
  },

  // Login user
  async login(username, password) {
    try {
      const response = await api.post('auth/login/', {
        username,
        password
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Logout user
  async logout() {
    try {
      const response = await api.post('auth/logout/')
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default authService