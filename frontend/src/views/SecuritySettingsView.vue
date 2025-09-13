<template>
  <div class="q-pa-md">
    <AppHeader title="Security Settings" />
    
    <div class="row justify-center">
      <div class="col-12 col-md-8 col-lg-6">
        <q-card class="q-pa-lg">
          <q-card-section>
            <div class="text-h5 q-mb-md">Two-Factor Authentication</div>
            <div class="text-body1 q-mb-lg text-grey-7">
              Add an extra layer of security to your account by requiring an authentication code from your mobile device when signing in.
            </div>

            <!-- 2FA Status -->
            <div v-if="!loading">
              <div v-if="!twoFactorEnabled" class="q-mb-lg">
                <q-icon name="security" size="3em" color="grey-5" class="q-mb-md" />
                <div class="text-h6 q-mb-sm">Two-factor authentication is not enabled</div>
                <div class="text-body2 text-grey-7 q-mb-lg">
                  Enable 2FA to protect your account with an additional security layer.
                </div>
                <q-btn 
                  color="primary" 
                  label="Enable 2FA" 
                  @click="startSetup"
                  :loading="setupLoading"
                />
              </div>

              <div v-else class="q-mb-lg">
                <q-icon name="verified" size="3em" color="green" class="q-mb-md" />
                <div class="text-h6 q-mb-sm text-green">Two-factor authentication is enabled</div>
                <div class="text-body2 text-grey-7 q-mb-lg">
                  Your account is protected with two-factor authentication.
                </div>
                <q-btn 
                  color="negative" 
                  outline
                  label="Disable 2FA" 
                  @click="showDisableDialog = true"
                />
              </div>
            </div>

            <!-- Loading -->
            <div v-else class="text-center q-py-lg">
              <q-spinner size="50px" />
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Setup 2FA Dialog -->
    <q-dialog v-model="showSetupDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Set up Two-Factor Authentication</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div v-if="setupStep === 'qr'">
            <div class="text-body1 q-mb-md">
              1. Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
            </div>
            <div class="text-center q-mb-md">
              <img :src="qrCodeUrl" alt="QR Code" style="max-width: 200px;" />
            </div>
            <div class="text-body2 text-grey-7 q-mb-md">
              Or enter this key manually: <code>{{ secretKey }}</code>
            </div>
            <div class="text-body1 q-mb-md">
              2. Enter the 6-digit verification code from your app:
            </div>
            <q-input
              v-model="verificationCode"
              label="Verification Code"
              outlined
              maxlength="6"
              :error="setupError !== ''"
              :error-message="setupError"
            />
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelSetup" />
          <q-btn 
            color="primary" 
            label="Verify & Enable" 
            @click="confirmSetup"
            :loading="confirmLoading"
            :disable="verificationCode.length !== 6"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Disable 2FA Dialog -->
    <q-dialog v-model="showDisableDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Disable Two-Factor Authentication</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-body1 q-mb-md">
            Are you sure you want to disable two-factor authentication? This will make your account less secure.
          </div>
          <div class="text-body1 q-mb-md">
            Please enter your password to confirm:
          </div>
          <q-input
            v-model="confirmPassword"
            label="Password"
            type="password"
            outlined
            :error="disableError !== ''"
            :error-message="disableError"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="showDisableDialog = false" />
          <q-btn 
            color="negative" 
            label="Disable 2FA" 
            @click="confirmDisable"
            :loading="disableLoading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import AppHeader from '@/components/AppHeader.vue'
import authService from '@/services/auth'

const $q = useQuasar()

// State
const loading = ref(false)
const twoFactorEnabled = ref(false)

// Setup dialog
const showSetupDialog = ref(false)
const setupStep = ref('qr')
const setupLoading = ref(false)
const confirmLoading = ref(false)
const qrCodeUrl = ref('')
const secretKey = ref('')
const deviceId = ref('')
const verificationCode = ref('')
const setupError = ref('')

// Disable dialog
const showDisableDialog = ref(false)
const disableLoading = ref(false)
const confirmPassword = ref('')
const disableError = ref('')

// Load 2FA status
const load2FAStatus = async () => {
  loading.value = true
  try {
    const response = await authService.get2FAStatus()
    twoFactorEnabled.value = response.has_2fa
  } catch (error) {
    console.error('Failed to load 2FA status:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to load 2FA status'
    })
  } finally {
    loading.value = false
  }
}

// Start 2FA setup
const startSetup = async () => {
  setupLoading.value = true
  try {
    const response = await authService.setup2FA()
    qrCodeUrl.value = response.qr_code
    secretKey.value = response.secret_key
    deviceId.value = response.device_id
    showSetupDialog.value = true
    setupStep.value = 'qr'
  } catch (error) {
    console.error('Failed to start 2FA setup:', error)
    $q.notify({
      type: 'negative',
      message: error.response?.data?.error || 'Failed to start 2FA setup'
    })
  } finally {
    setupLoading.value = false
  }
}

// Confirm 2FA setup
const confirmSetup = async () => {
  setupError.value = ''
  confirmLoading.value = true
  try {
    await authService.confirm2FA(verificationCode.value, deviceId.value)
    showSetupDialog.value = false
    twoFactorEnabled.value = true
    $q.notify({
      type: 'positive',
      message: 'Two-factor authentication enabled successfully'
    })
  } catch (error) {
    console.error('Failed to confirm 2FA setup:', error)
    setupError.value = error.response?.data?.error || 'Invalid verification code'
  } finally {
    confirmLoading.value = false
  }
}

// Cancel setup
const cancelSetup = () => {
  showSetupDialog.value = false
  verificationCode.value = ''
  setupError.value = ''
}

// Confirm disable
const confirmDisable = async () => {
  disableError.value = ''
  disableLoading.value = true
  try {
    await authService.disable2FA(confirmPassword.value)
    showDisableDialog.value = false
    twoFactorEnabled.value = false
    confirmPassword.value = ''
    $q.notify({
      type: 'positive',
      message: 'Two-factor authentication disabled'
    })
  } catch (error) {
    console.error('Failed to disable 2FA:', error)
    disableError.value = error.response?.data?.error || 'Failed to disable 2FA'
  } finally {
    disableLoading.value = false
  }
}

onMounted(() => {
  load2FAStatus()
})
</script>