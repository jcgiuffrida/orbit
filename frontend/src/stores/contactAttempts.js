import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { contactAttemptsService } from '@/services/contactAttempts'

export const useContactAttemptsStore = defineStore('contactAttempts', () => {
  const contactAttempts = ref([])
  const selectedContactAttempt = ref(null)
  const isLoading = ref(false)
  const hasError = ref(false)
  const error = ref(null)
  const lastFetched = ref(null)

  const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

  const isCacheValid = computed(() => {
    if (!lastFetched.value) return false
    return (Date.now() - lastFetched.value) < CACHE_DURATION
  })

  const getContactAttemptsList = computed(() => contactAttempts.value)
  const contactAttemptsCount = computed(() => contactAttempts.value.length)

  const setLoading = (loading) => {
    isLoading.value = loading
    if (loading) {
      hasError.value = false
      error.value = null
    }
  }

  const setError = (err) => {
    hasError.value = true
    error.value = err
    isLoading.value = false
  }

  const clearError = () => {
    hasError.value = false
    error.value = null
  }

  const fetchContactAttempts = async (forceRefresh = false) => {
    if (!forceRefresh && isCacheValid.value && contactAttempts.value.length > 0) {
      return contactAttempts.value
    }

    setLoading(true)
    clearError()

    try {
      const data = await contactAttemptsService.fetchContactAttempts()
      contactAttempts.value = data
      lastFetched.value = Date.now()
      return data
    } catch (err) {
      console.error('Failed to fetch contact attempts:', err)
      setError('Failed to load contact attempts')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchContactAttemptsForPerson = async (personId) => {
    setLoading(true)
    clearError()

    try {
      const data = await contactAttemptsService.fetchContactAttemptsForPerson(personId)
      return data
    } catch (err) {
      console.error('Failed to fetch contact attempts for person:', err)
      setError('Failed to load contact attempts')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchContactAttemptById = async (id) => {
    setLoading(true)
    clearError()

    try {
      const data = await contactAttemptsService.fetchContactAttemptById(id)
      selectedContactAttempt.value = data
      
      const existingIndex = contactAttempts.value.findIndex(c => c.id === id)
      if (existingIndex >= 0) {
        contactAttempts.value[existingIndex] = data
      }
      
      return data
    } catch (err) {
      console.error('Failed to fetch contact attempt:', err)
      setError('Failed to load contact attempt details')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const createContactAttempt = async (contactAttemptData) => {
    setLoading(true)
    clearError()

    try {
      const newContactAttempt = await contactAttemptsService.createContactAttempt(contactAttemptData)
      contactAttempts.value.unshift(newContactAttempt)
      lastFetched.value = Date.now()
      return newContactAttempt
    } catch (err) {
      console.error('Failed to create contact attempt:', err)
      setError('Failed to create contact attempt')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const updateContactAttempt = async (id, contactAttemptData) => {
    setLoading(true)
    clearError()

    try {
      const updatedContactAttempt = await contactAttemptsService.updateContactAttempt(id, contactAttemptData)
      
      const index = contactAttempts.value.findIndex(c => c.id === id)
      if (index >= 0) {
        contactAttempts.value[index] = updatedContactAttempt
      }
      
      if (selectedContactAttempt.value?.id === id) {
        selectedContactAttempt.value = updatedContactAttempt
      }
      
      return updatedContactAttempt
    } catch (err) {
      console.error('Failed to update contact attempt:', err)
      setError('Failed to update contact attempt')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const deleteContactAttempt = async (id) => {
    setLoading(true)
    clearError()

    try {
      await contactAttemptsService.deleteContactAttempt(id)
      
      contactAttempts.value = contactAttempts.value.filter(c => c.id !== id)
      
      if (selectedContactAttempt.value?.id === id) {
        selectedContactAttempt.value = null
      }
    } catch (err) {
      console.error('Failed to delete contact attempt:', err)
      setError('Failed to delete contact attempt')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const clearSelectedContactAttempt = () => {
    selectedContactAttempt.value = null
  }

  const invalidateCache = () => {
    lastFetched.value = null
  }

  return {
    contactAttempts,
    selectedContactAttempt,
    isLoading,
    hasError,
    error,
    getContactAttemptsList,
    contactAttemptsCount,
    isCacheValid,
    fetchContactAttempts,
    fetchContactAttemptsForPerson,
    fetchContactAttemptById,
    createContactAttempt,
    updateContactAttempt,
    deleteContactAttempt,
    clearSelectedContactAttempt,
    invalidateCache
  }
})