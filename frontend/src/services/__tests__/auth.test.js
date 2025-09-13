import { describe, it, expect, vi, beforeEach } from 'vitest'
import authService from '../auth'

// Mock the api module
vi.mock('../api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  }
}))

// Get reference to the mocked api
import api from '../api'
const mockApi = vi.mocked(api)

describe('AuthService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getCurrentUser', () => {
    it('should return user data when authenticated', async () => {
      const userData = {
        id: 1,
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        has_2fa: false
      }

      mockApi.get.mockResolvedValue({ data: userData })

      const result = await authService.getCurrentUser()
      
      expect(mockApi.get).toHaveBeenCalledWith('auth/user/')
      expect(result).toEqual(userData)
    })

    it('should return null when user is not authenticated', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 403 }
      })

      const result = await authService.getCurrentUser()
      
      expect(result).toBeNull()
    })

    it('should throw error for other errors', async () => {
      const error = { response: { status: 500 } }
      mockApi.get.mockRejectedValue(error)

      await expect(authService.getCurrentUser()).rejects.toThrow()
    })
  })

  describe('login', () => {
    it('should login successfully without 2FA', async () => {
      const loginResponse = {
        success: true,
        user: {
          id: 1,
          username: 'testuser',
          first_name: 'Test',
          last_name: 'User',
          has_2fa: false
        }
      }

      mockApi.post.mockResolvedValue({ data: loginResponse })

      const result = await authService.login('testuser', 'password123')
      
      expect(mockApi.post).toHaveBeenCalledWith('auth/login/', {
        username: 'testuser',
        password: 'password123',
        otp_token: null
      })
      expect(result).toEqual(loginResponse)
    })

    it('should login successfully with 2FA token', async () => {
      const loginResponse = {
        success: true,
        user: {
          id: 1,
          username: 'testuser',
          first_name: 'Test',
          last_name: 'User',
          has_2fa: true
        }
      }

      mockApi.post.mockResolvedValue({ data: loginResponse })

      const result = await authService.login('testuser', 'password123', '123456')
      
      expect(mockApi.post).toHaveBeenCalledWith('auth/login/', {
        username: 'testuser',
        password: 'password123',
        otp_token: '123456'
      })
      expect(result).toEqual(loginResponse)
    })

    it('should handle login errors', async () => {
      const error = {
        response: {
          data: { error: 'Invalid credentials' }
        }
      }

      mockApi.post.mockRejectedValue(error)

      await expect(authService.login('testuser', 'wrongpassword'))
        .rejects.toThrow()
    })
  })

  describe('logout', () => {
    it('should logout successfully', async () => {
      const logoutResponse = { success: true }
      mockApi.post.mockResolvedValue({ data: logoutResponse })

      const result = await authService.logout()
      
      expect(mockApi.post).toHaveBeenCalledWith('auth/logout/')
      expect(result).toEqual(logoutResponse)
    })

    it('should handle logout errors', async () => {
      const error = new Error('Network error')
      mockApi.post.mockRejectedValue(error)

      await expect(authService.logout()).rejects.toThrow('Network error')
    })
  })

  describe('get2FAStatus', () => {
    it('should return 2FA status', async () => {
      const statusResponse = {
        has_2fa: true,
        device_count: 1
      }

      mockApi.get.mockResolvedValue({ data: statusResponse })

      const result = await authService.get2FAStatus()
      
      expect(mockApi.get).toHaveBeenCalledWith('auth/2fa/status/')
      expect(result).toEqual(statusResponse)
    })
  })

  describe('setup2FA', () => {
    it('should setup 2FA successfully', async () => {
      const setupResponse = {
        success: true,
        qr_code: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==',
        secret_key: 'ABCDEFGHIJKLMNOP',
        device_id: 123
      }

      mockApi.post.mockResolvedValue({ data: setupResponse })

      const result = await authService.setup2FA()
      
      expect(mockApi.post).toHaveBeenCalledWith('auth/2fa/setup/')
      expect(result).toEqual(setupResponse)
    })

    it('should handle setup errors', async () => {
      const error = {
        response: {
          data: { error: 'Two-factor authentication is already enabled' }
        }
      }

      mockApi.post.mockRejectedValue(error)

      await expect(authService.setup2FA()).rejects.toThrow()
    })
  })

  describe('confirm2FA', () => {
    it('should confirm 2FA successfully', async () => {
      const confirmResponse = {
        success: true,
        message: 'Two-factor authentication enabled'
      }

      mockApi.post.mockResolvedValue({ data: confirmResponse })

      const result = await authService.confirm2FA('123456', 123)
      
      expect(mockApi.post).toHaveBeenCalledWith('auth/2fa/confirm/', {
        token: '123456',
        device_id: 123
      })
      expect(result).toEqual(confirmResponse)
    })

    it('should handle confirmation errors', async () => {
      const error = {
        response: {
          data: { error: 'Invalid token' }
        }
      }

      mockApi.post.mockRejectedValue(error)

      await expect(authService.confirm2FA('000000', 123)).rejects.toThrow()
    })
  })

  describe('disable2FA', () => {
    it('should disable 2FA successfully', async () => {
      const disableResponse = {
        success: true,
        message: 'Two-factor authentication disabled'
      }

      mockApi.post.mockResolvedValue({ data: disableResponse })

      const result = await authService.disable2FA('password123')
      
      expect(mockApi.post).toHaveBeenCalledWith('auth/2fa/disable/', {
        password: 'password123'
      })
      expect(result).toEqual(disableResponse)
    })

    it('should handle disable errors', async () => {
      const error = {
        response: {
          data: { error: 'Invalid password' }
        }
      }

      mockApi.post.mockRejectedValue(error)

      await expect(authService.disable2FA('wrongpassword')).rejects.toThrow()
    })
  })
})