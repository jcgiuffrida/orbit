import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { setActivePinia, createPinia } from 'pinia'
import { Quasar } from 'quasar'
import LoginView from '../LoginView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/login', name: 'login', component: LoginView }
  ]
})

const createWrapper = (options = {}) => {
  return mount(LoginView, {
    global: {
      plugins: [router, Quasar, createPinia()],
      stubs: {
        'q-card': { template: '<div class="q-card"><slot /></div>' },
        'q-card-section': { template: '<div class="q-card-section"><slot /></div>' },
        'q-form': { 
          template: '<form @submit.prevent="handleSubmit"><slot /></form>',
          methods: {
            handleSubmit(e) {
              this.$emit('submit', e)
            }
          }
        },
        'q-input': {
          template: '<input :value="modelValue" :type="type" :data-label="label" @input="handleInput" />',
          props: ['modelValue', 'type', 'label', 'outlined', 'required', 'disable', 'placeholder', 'maxlength'],
          emits: ['update:modelValue'],
          methods: {
            handleInput(e) {
              this.$emit('update:modelValue', e.target.value)
            }
          }
        },
        'q-btn': {
          template: '<button :disabled="loading || disable" @click="$emit(\'click\')"><slot>{{ label }}</slot></button>',
          props: ['loading', 'disable', 'label', 'type', 'color', 'class']
        },
        'q-banner': { template: '<div class="q-banner"><slot /></div>' }
      }
    },
    ...options
  })
}

describe('LoginView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    
    // Ensure authStore.login always returns a valid response by default
    const authStore = useAuthStore()
    authStore.login = vi.fn().mockResolvedValue({ 
      success: false, 
      error: 'Mock not configured for this test' 
    })
  })

  it('renders login form correctly', () => {
    const wrapper = createWrapper()

    expect(wrapper.find('h4').exists()).toBe(false) // No h4 in our template
    expect(wrapper.text()).toContain('Orbit Login')
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button').text()).toBe('Login')
  })

  it('shows validation error when fields are empty', async () => {
    const wrapper = createWrapper()

    // Try to submit with empty fields
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain('Please enter username and password')
  })

  it('calls login when form is submitted with valid data', async () => {
    const wrapper = createWrapper()
    const authStore = useAuthStore()
    
    // Mock successful login
    authStore.login = vi.fn().mockResolvedValue({ success: true })
    
    // Fill in the form
    const usernameInput = wrapper.find('input[data-label="Username"]')
    const passwordInput = wrapper.find('input[type="password"]')
    
    await usernameInput.setValue('testuser')
    await passwordInput.setValue('password123')

    // Submit form
    await wrapper.find('form').trigger('submit')

    expect(authStore.login).toHaveBeenCalledWith('testuser', 'password123', '')
  })

  it('shows error message on login failure', async () => {
    const wrapper = createWrapper()
    const authStore = useAuthStore()
    
    // Mock failed login
    authStore.login = vi.fn().mockResolvedValue({ 
      success: false, 
      error: 'Invalid credentials' 
    })
    
    // Fill in the form
    const usernameInput = wrapper.find('input[data-label="Username"]')
    const passwordInput = wrapper.find('input[type="password"]')
    
    await usernameInput.setValue('testuser')
    await passwordInput.setValue('wrongpassword')

    // Submit form
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Invalid credentials')
  })

  it('shows 2FA input when 2FA is required', async () => {
    const wrapper = createWrapper()
    const authStore = useAuthStore()
    
    // Mock login requiring 2FA
    authStore.login = vi.fn().mockResolvedValue({ 
      success: false, 
      requires_2fa: true,
      error: 'Two-factor authentication required'
    })
    
    // Fill in the form
    const usernameInput = wrapper.find('input[data-label="Username"]')
    const passwordInput = wrapper.find('input[type="password"]')
    
    await usernameInput.setValue('testuser')
    await passwordInput.setValue('password123')

    // Submit form
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    // Should show OTP field
    expect(wrapper.find('input[data-label="Authentication Code"]').exists()).toBe(true)
    expect(wrapper.find('button').text()).toBe('Complete Login')
    expect(wrapper.text()).toContain('Please enter the 6-digit code from your authenticator app')
  })

  it('requires OTP token when 2FA field is shown', async () => {
    const wrapper = createWrapper()
    const authStore = useAuthStore()
    
    // Mock login requiring 2FA
    authStore.login = vi.fn().mockResolvedValue({ 
      success: false, 
      requires_2fa: true,
      error: 'Two-factor authentication required'
    })
    
    // Fill in the form and trigger 2FA
    const usernameInput = wrapper.find('input[data-label="Username"]')
    const passwordInput = wrapper.find('input[type="password"]')
    
    await usernameInput.setValue('testuser')
    await passwordInput.setValue('password123')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    // Clear the mock to test second submission
    authStore.login.mockClear()

    // Try to submit without OTP token
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain('Please enter the authentication code')
    expect(authStore.login).not.toHaveBeenCalled()
  })

  it('completes 2FA login successfully', async () => {
    const wrapper = createWrapper()
    const authStore = useAuthStore()
    const mockPush = vi.fn()
    wrapper.vm.$router.push = mockPush
    
    // Mock login requiring 2FA first
    authStore.login = vi.fn()
      .mockResolvedValueOnce({ 
        success: false, 
        requires_2fa: true,
        error: 'Two-factor authentication required'
      })
      .mockResolvedValueOnce({ 
        success: true,
        user: { username: 'testuser', has_2fa: true }
      })
    
    // Fill in the form and trigger 2FA
    const usernameInput = wrapper.find('input[data-label="Username"]')
    const passwordInput = wrapper.find('input[type="password"]')
    
    await usernameInput.setValue('testuser')
    await passwordInput.setValue('password123')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    // Now fill in OTP and submit
    const otpInput = wrapper.find('input[data-label="Authentication Code"]')
    await otpInput.setValue('123456')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(authStore.login).toHaveBeenLastCalledWith('testuser', 'password123', '123456')
    expect(mockPush).toHaveBeenCalledWith({ name: 'home' })
  })


  it('redirects to home on successful login', async () => {
    const wrapper = createWrapper()
    const authStore = useAuthStore()
    const mockPush = vi.fn()
    wrapper.vm.$router.push = mockPush
    
    // Mock successful login
    authStore.login = vi.fn().mockResolvedValue({ 
      success: true,
      user: { username: 'testuser', has_2fa: false }
    })
    
    // Fill in the form
    const usernameInput = wrapper.find('input[data-label="Username"]')
    const passwordInput = wrapper.find('input[type="password"]')
    
    await usernameInput.setValue('testuser')
    await passwordInput.setValue('password123')

    // Submit form
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(mockPush).toHaveBeenCalledWith({ name: 'home' })
  })

  it('resets error state when credentials change after 2FA error', async () => {
    const wrapper = createWrapper()
    const authStore = useAuthStore()
    
    // Mock login failure first
    authStore.login = vi.fn().mockResolvedValue({ 
      success: false, 
      error: 'Invalid credentials' 
    })
    
    // Fill in the form with wrong credentials
    const usernameInput = wrapper.find('input[data-label="Username"]')
    const passwordInput = wrapper.find('input[type="password"]')
    
    await usernameInput.setValue('testuser')
    await passwordInput.setValue('wrongpassword')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Invalid credentials')

    // Now mock successful login requiring 2FA
    authStore.login.mockResolvedValue({ 
      success: false, 
      requires_2fa: true,
      error: 'Two-factor authentication required'
    })

    // Change password and submit again
    await passwordInput.setValue('correctpassword')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    // Error should be cleared and 2FA field should show
    expect(wrapper.text()).not.toContain('Invalid credentials')
    expect(wrapper.find('input[data-label="Authentication Code"]').exists()).toBe(true)
  })
})