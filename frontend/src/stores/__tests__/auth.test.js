import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import authService from '@/services/auth'

// Mock the auth service
vi.mock('@/services/auth')
const mockedAuthService = vi.mocked(authService)

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('checkAuth', () => {
    it('should set user when authentication check succeeds', async () => {
      const userData = {
        id: 1,
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        has_2fa: false
      }

      mockedAuthService.getCurrentUser.mockResolvedValue(userData)
      
      const store = useAuthStore()
      await store.checkAuth()

      expect(store.user).toEqual(userData)
      expect(store.isAuthenticated).toBe(true)
      expect(store.initialized).toBe(true)
      expect(store.loading).toBe(false)
    })

    it('should clear user when authentication check fails', async () => {
      mockedAuthService.getCurrentUser.mockRejectedValue(new Error('Auth failed'))
      
      const store = useAuthStore()
      await store.checkAuth()

      expect(store.user).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(store.initialized).toBe(true)
      expect(store.loading).toBe(false)
    })
  })

  describe('login', () => {
    it('should login successfully without 2FA', async () => {
      const userData = {
        id: 1,
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        has_2fa: false
      }

      mockedAuthService.login.mockResolvedValue({
        success: true,
        user: userData
      })

      const store = useAuthStore()
      const result = await store.login('testuser', 'password123')

      expect(result.success).toBe(true)
      expect(store.user).toEqual(userData)
      expect(store.isAuthenticated).toBe(true)
    })

    it('should handle login requiring 2FA', async () => {
      mockedAuthService.login.mockResolvedValue({
        success: false,
        requires_2fa: true,
        error: 'Two-factor authentication required'
      })

      const store = useAuthStore()
      const result = await store.login('testuser', 'password123')

      expect(result.success).toBe(false)
      expect(result.requires_2fa).toBe(true)
      expect(result.error).toBe('Two-factor authentication required')
      expect(store.user).toBeNull()
    })

    it('should login successfully with 2FA token', async () => {
      const userData = {
        id: 1,
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        has_2fa: true
      }

      mockedAuthService.login.mockResolvedValue({
        success: true,
        user: userData
      })

      const store = useAuthStore()
      const result = await store.login('testuser', 'password123', '123456')

      expect(result.success).toBe(true)
      expect(store.user).toEqual(userData)
      expect(store.isAuthenticated).toBe(true)
    })

    it('should handle invalid 2FA token', async () => {
      mockedAuthService.login.mockResolvedValue({
        success: false,
        error: 'Invalid authentication token'
      })

      const store = useAuthStore()
      const result = await store.login('testuser', 'password123', '000000')

      expect(result.success).toBe(false)
      expect(result.error).toBe('Invalid authentication token')
      expect(store.user).toBeNull()
    })

    it('should handle login errors with 2FA requirement from exception', async () => {
      mockedAuthService.login.mockRejectedValue({
        response: {
          data: {
            requires_2fa: true,
            error: 'Two-factor authentication required'
          }
        }
      })

      const store = useAuthStore()
      const result = await store.login('testuser', 'password123')

      expect(result.success).toBe(false)
      expect(result.requires_2fa).toBe(true)
      expect(result.error).toBe('Two-factor authentication required')
    })

    it('should handle general login errors', async () => {
      mockedAuthService.login.mockRejectedValue({
        response: {
          data: {
            error: 'Invalid credentials'
          }
        }
      })

      const store = useAuthStore()
      const result = await store.login('testuser', 'wrongpassword')

      expect(result.success).toBe(false)
      expect(result.error).toBe('Invalid credentials')
      expect(store.user).toBeNull()
    })

    it('should handle network errors', async () => {
      mockedAuthService.login.mockRejectedValue(new Error('Network error'))

      const store = useAuthStore()
      const result = await store.login('testuser', 'password123')

      expect(result.success).toBe(false)
      expect(result.error).toBe('Login failed')
      expect(store.user).toBeNull()
    })
  })

  describe('logout', () => {
    it('should logout successfully', async () => {
      mockedAuthService.logout.mockResolvedValue({ success: true })

      const store = useAuthStore()
      // Set a user first
      store.user = { id: 1, username: 'testuser' }
      
      await store.logout()

      expect(store.user).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(mockedAuthService.logout).toHaveBeenCalled()
    })

    it('should clear user even when logout fails', async () => {
      mockedAuthService.logout.mockRejectedValue(new Error('Logout failed'))

      const store = useAuthStore()
      // Set a user first
      store.user = { id: 1, username: 'testuser' }
      
      await store.logout()

      expect(store.user).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('clearAuth', () => {
    it('should clear authentication state', () => {
      const store = useAuthStore()
      store.user = { id: 1, username: 'testuser' }
      store.initialized = true

      store.clearAuth()

      expect(store.user).toBeNull()
      expect(store.initialized).toBe(false)
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('computed properties', () => {
    it('should correctly compute isAuthenticated', () => {
      const store = useAuthStore()
      
      expect(store.isAuthenticated).toBe(false)
      
      store.user = { id: 1, username: 'testuser' }
      expect(store.isAuthenticated).toBe(true)
      
      store.user = null
      expect(store.isAuthenticated).toBe(false)
    })

    it('should correctly compute isLoading', () => {
      const store = useAuthStore()
      
      expect(store.isLoading).toBe(false)
      
      store.loading = true
      expect(store.isLoading).toBe(true)
      
      store.loading = false
      expect(store.isLoading).toBe(false)
    })
  })
})