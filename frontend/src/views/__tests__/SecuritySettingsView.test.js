import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { Quasar, Notify } from 'quasar'
import SecuritySettingsView from '../SecuritySettingsView.vue'
import authService from '@/services/auth'

// Mock the auth service
vi.mock('@/services/auth')
const mockedAuthService = vi.mocked(authService)

// Mock $q.notify
const mockNotify = vi.fn()
vi.mock('quasar', async () => {
  const actual = await vi.importActual('quasar')
  return {
    ...actual,
    useQuasar: () => ({
      notify: mockNotify
    })
  }
})

const createWrapper = (options = {}) => {
  return mount(SecuritySettingsView, {
    global: {
      plugins: [Quasar, createPinia()],
      stubs: {
        'AppHeader': { template: '<div class="app-header">{{ title }}</div>', props: ['title'] },
        'q-card': { template: '<div class="q-card"><slot /></div>' },
        'q-card-section': { template: '<div class="q-card-section"><slot /></div>' },
        'q-btn': {
          template: '<button :disabled="loading || disable" @click="$emit(\'click\')"><slot>{{ label }}</slot></button>',
          props: ['loading', 'disable', 'label', 'color', 'outline'],
          emits: ['click']
        },
        'q-icon': { template: '<i class="q-icon">{{ name }}</i>', props: ['name', 'size', 'color'] },
        'q-spinner': { template: '<div class="q-spinner" />', props: ['size'] },
        'q-dialog': {
          template: '<div v-if="modelValue" class="q-dialog"><slot /></div>',
          props: ['modelValue', 'persistent'],
          emits: ['update:modelValue']
        },
        'q-input': {
          template: '<input v-model="modelValue" :type="type" :label="label" @input="$emit(\'update:modelValue\', $event.target.value)" />',
          props: ['modelValue', 'type', 'label', 'outlined', 'maxlength', 'error', 'errorMessage'],
          emits: ['update:modelValue']
        },
        'q-card-actions': { template: '<div class="q-card-actions"><slot /></div>' }
      }
    },
    ...options
  })
}

describe('SecuritySettingsView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockNotify.mockClear()
  })

  it('renders security settings page correctly', () => {
    mockedAuthService.get2FAStatus.mockResolvedValue({ has_2fa: false, device_count: 0 })
    
    const wrapper = createWrapper()

    expect(wrapper.find('.app-header').text()).toBe('Security Settings')
    expect(wrapper.text()).toContain('Two-Factor Authentication')
    expect(wrapper.text()).toContain('Add an extra layer of security')
  })

  it('shows 2FA disabled state when 2FA is not enabled', async () => {
    mockedAuthService.get2FAStatus.mockResolvedValue({ has_2fa: false, device_count: 0 })
    
    const wrapper = createWrapper()
    await flushPromises()

    expect(wrapper.text()).toContain('Two-factor authentication is not enabled')
    expect(wrapper.text()).toContain('Enable 2FA to protect your account')
    expect(wrapper.find('button').text()).toBe('Enable 2FA')
  })

  it('shows 2FA enabled state when 2FA is enabled', async () => {
    mockedAuthService.get2FAStatus.mockResolvedValue({ has_2fa: true, device_count: 1 })
    
    const wrapper = createWrapper()
    await flushPromises()

    expect(wrapper.text()).toContain('Two-factor authentication is enabled')
    expect(wrapper.text()).toContain('Your account is protected with two-factor authentication')
    expect(wrapper.find('button').text()).toBe('Disable 2FA')
  })

  it('starts 2FA setup when enable button is clicked', async () => {
    mockedAuthService.get2FAStatus.mockResolvedValue({ has_2fa: false, device_count: 0 })
    mockedAuthService.setup2FA.mockResolvedValue({
      success: true,
      qr_code: 'data:image/png;base64,testimage',
      secret_key: 'ABCDEFGHIJKLMNOP',
      device_id: 123
    })
    
    const wrapper = createWrapper()
    await flushPromises()

    const enableButton = wrapper.find('button')
    await enableButton.trigger('click')
    await flushPromises()

    expect(mockedAuthService.setup2FA).toHaveBeenCalled()
    expect(wrapper.find('.q-dialog').exists()).toBe(true)
    expect(wrapper.text()).toContain('Set up Two-Factor Authentication')
    expect(wrapper.find('img').attributes('src')).toBe('data:image/png;base64,testimage')
    expect(wrapper.text()).toContain('ABCDEFGHIJKLMNOP')
  })

  it('handles 2FA setup error', async () => {
    mockedAuthService.get2FAStatus.mockResolvedValue({ has_2fa: false, device_count: 0 })
    mockedAuthService.setup2FA.mockRejectedValue({
      response: { data: { error: 'Two-factor authentication is already enabled' } }
    })
    
    const wrapper = createWrapper()
    await flushPromises()

    const enableButton = wrapper.find('button')
    await enableButton.trigger('click')
    await flushPromises()

    expect(mockNotify).toHaveBeenCalledWith({
      type: 'negative',
      message: 'Two-factor authentication is already enabled'
    })
  })

  it('confirms 2FA setup successfully', async () => {
    mockedAuthService.get2FAStatus.mockResolvedValue({ has_2fa: false, device_count: 0 })
    mockedAuthService.setup2FA.mockResolvedValue({
      success: true,
      qr_code: 'data:image/png;base64,testimage',
      secret_key: 'ABCDEFGHIJKLMNOP',
      device_id: 123
    })
    mockedAuthService.confirm2FA.mockResolvedValue({
      success: true,
      message: 'Two-factor authentication enabled'
    })
    
    const wrapper = createWrapper()
    await flushPromises()

    // Start setup
    const enableButton = wrapper.find('button')
    await enableButton.trigger('click')
    await flushPromises()

    // Enter verification code
    const input = wrapper.find('input[label="Verification Code"]')
    await input.setValue('123456')

    // Confirm setup
    const confirmButton = wrapper.findAll('button').find(btn => btn.text() === 'Verify & Enable')
    await confirmButton.trigger('click')
    await flushPromises()

    expect(mockedAuthService.confirm2FA).toHaveBeenCalledWith('123456', 123)
    expect(mockNotify).toHaveBeenCalledWith({
      type: 'positive',
      message: 'Two-factor authentication enabled successfully'
    })
    expect(wrapper.find('.q-dialog').exists()).toBe(false)
  })

  it('cancels 2FA setup', async () => {
    mockedAuthService.get2FAStatus.mockResolvedValue({ has_2fa: false, device_count: 0 })
    mockedAuthService.setup2FA.mockResolvedValue({
      success: true,
      qr_code: 'data:image/png;base64,testimage',
      secret_key: 'ABCDEFGHIJKLMNOP',
      device_id: 123
    })
    
    const wrapper = createWrapper()
    await flushPromises()

    // Start setup
    const enableButton = wrapper.find('button')
    await enableButton.trigger('click')
    await flushPromises()

    // Cancel setup
    const cancelButton = wrapper.findAll('button').find(btn => btn.text() === 'Cancel')
    await cancelButton.trigger('click')
    await flushPromises()

    expect(wrapper.find('.q-dialog').exists()).toBe(false)
  })

  it('shows disable 2FA dialog', async () => {
    mockedAuthService.get2FAStatus.mockResolvedValue({ has_2fa: true, device_count: 1 })
    
    const wrapper = createWrapper()
    await flushPromises()

    const disableButton = wrapper.find('button')
    await disableButton.trigger('click')
    await flushPromises()

    expect(wrapper.find('.q-dialog').exists()).toBe(true)
    expect(wrapper.text()).toContain('Disable Two-Factor Authentication')
    expect(wrapper.text()).toContain('Please enter your password to confirm')
  })

  it('handles 2FA status loading error', async () => {
    mockedAuthService.get2FAStatus.mockRejectedValue(new Error('Network error'))
    
    const wrapper = createWrapper()
    await flushPromises()

    expect(mockNotify).toHaveBeenCalledWith({
      type: 'negative',
      message: 'Failed to load 2FA status'
    })
  })

  it('disables verify button when verification code is not 6 digits', async () => {
    mockedAuthService.get2FAStatus.mockResolvedValue({ has_2fa: false, device_count: 0 })
    mockedAuthService.setup2FA.mockResolvedValue({
      success: true,
      qr_code: 'data:image/png;base64,testimage',
      secret_key: 'ABCDEFGHIJKLMNOP',
      device_id: 123
    })
    
    const wrapper = createWrapper()
    await flushPromises()

    // Start setup
    const enableButton = wrapper.find('button')
    await enableButton.trigger('click')
    await flushPromises()

    // Enter incomplete verification code
    const input = wrapper.find('input[label="Verification Code"]')
    await input.setValue('123')

    const confirmButton = wrapper.findAll('button').find(btn => btn.text() === 'Verify & Enable')
    expect(confirmButton.attributes('disabled')).toBeDefined()

    // Complete the code
    await input.setValue('123456')
    expect(confirmButton.attributes('disabled')).toBeUndefined()
  })
})