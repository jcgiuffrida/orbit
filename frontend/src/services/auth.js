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

  // Login user (with 2FA support)
  async login(username, password, otpToken = null) {
    try {
      const response = await api.post('auth/login/', {
        username,
        password,
        otp_token: otpToken
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
  },

  // 2FA Management
  async get2FAStatus() {
    try {
      const response = await api.get('auth/2fa/status/')
      return response.data
    } catch (error) {
      throw error
    }
  },

  async setup2FA() {
    try {
      const response = await api.post('auth/2fa/setup/')
      return response.data
    } catch (error) {
      throw error
    }
  },

  async confirm2FA(token, deviceId) {
    try {
      const response = await api.post('auth/2fa/confirm/', {
        token,
        device_id: deviceId
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  async disable2FA(password) {
    try {
      const response = await api.post('auth/2fa/disable/', {
        password
      })
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default authService