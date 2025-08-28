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
          <q-btn
            type="submit"
            color="primary"
            class="full-width"
            :loading="authStore.isLoading"
            label="Login"
          />
        </q-form>
        <q-banner v-if="error" class="bg-negative text-white q-mt-md" rounded>
          {{ error }}
        </q-banner>
      </q-card-section>
    </q-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const username = ref('')
    const password = ref('')
    const error = ref('')

    const handleSubmit = async () => {
      error.value = ''
      
      if (!username.value || !password.value) {
        error.value = 'Please enter username and password'
        return
      }

      const result = await authStore.login(username.value, password.value)
      
      if (result.success) {
        router.push({ name: 'home' })
      } else {
        error.value = result.error
      }
    }

    return {
      username,
      password,
      error,
      authStore,
      handleSubmit
    }
  }
}
</script>