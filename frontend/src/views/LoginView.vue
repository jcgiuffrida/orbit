<template>
  <div class="q-pa-md flex flex-center" style="min-height: 100vh">
    <q-card class="q-pa-lg" style="width: 100%; max-width: 400px">
      <q-card-section>
        <div class="text-h4 text-center q-mb-md">Orbit Login</div>
        <q-form @submit="handleSubmit" class="q-gutter-md">
          <q-input
            v-model="username"
            autofocus
            label="Username"
            outlined
            required
            :disable="authStore.isLoading"
          />
          <q-input
            v-model="password"
            label="Password"
            type="password"
            outlined
            required
            :disable="authStore.isLoading"
          />
          <q-input
            v-if="showOtpField"
            v-model="otpToken"
            label="Authentication Code"
            outlined
            required
            :disable="authStore.isLoading"
            placeholder="Enter 6-digit code from your authenticator app"
            maxlength="6"
          />
          <q-btn
            type="submit"
            color="primary"
            class="full-width"
            :loading="authStore.isLoading"
            :label="showOtpField ? 'Complete Login' : 'Login'"
          />
        </q-form>
        <q-banner v-if="error" class="bg-negative text-white q-mt-md" rounded>
          {{ error }}
        </q-banner>
        <q-banner v-if="showOtpField && !error" class="bg-info text-white q-mt-md" rounded>
          Please enter the 6-digit code from your authenticator app to complete login.
        </q-banner>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const otpToken = ref('')
const error = ref('')
const showOtpField = ref(false)

const handleSubmit = async () => {
  error.value = ''
  
  if (!username.value || !password.value) {
    error.value = 'Please enter username and password'
    return
  }

  if (showOtpField.value && !otpToken.value) {
    error.value = 'Please enter the authentication code'
    return
  }

  const result = await authStore.login(username.value, password.value, otpToken.value)
  
  if (result?.success) {
    router.push({ name: 'home' })
  } else if (result?.requires_2fa) {
    showOtpField.value = true
    error.value = ''
  } else {
    error.value = result ? result.error : 'Login failed'
    // Only hide OTP field for credential errors, not for invalid 2FA token errors
    if (!showOtpField.value) {
      showOtpField.value = false
    }
  }
}
</script>