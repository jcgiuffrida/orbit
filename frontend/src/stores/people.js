import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import peopleService from '@/services/people'

export const usePeopleStore = defineStore('people', () => {
  // State
  const people = ref([])
  const loading = ref(false)
  const error = ref(null)
  const lastFetch = ref(null)
  const selectedPerson = ref(null)

  // Cache configuration
  const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes in milliseconds

  // Getters
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => !!error.value)
  const peopleCount = computed(() => people.value.length)
  
  const getPeopleList = computed(() => people.value)
  
  const getPersonById = computed(() => {
    return (id) => people.value.find(person => person.id === id)
  })

  // Check if cache is still valid
  const isCacheValid = computed(() => {
    if (!lastFetch.value) return false
    const now = new Date().getTime()
    return (now - lastFetch.value) < CACHE_DURATION
  })

  // Actions
  const clearError = () => {
    error.value = null
  }

  const setLoading = (state) => {
    loading.value = state
  }

  const setError = (errorMessage) => {
    error.value = errorMessage
    loading.value = false
  }

  // Fetch all people (with caching)
  const fetchPeople = async (force = false) => {
    // If cache is valid and not forced, return cached data
    if (!force && isCacheValid.value && people.value.length > 0) {
      return people.value
    }

    setLoading(true)
    clearError()

    try {
      const response = await peopleService.getAll()
      people.value = response.results || response
      lastFetch.value = new Date().getTime()
      return people.value
    } catch (err) {
      console.error('Error fetching people:', err)
      setError(err.response?.data?.message || 'Failed to load people')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Fetch single person by ID
  const fetchPersonById = async (id, force = false) => {
    // Try to get from cache first
    const cachedPerson = getPersonById.value(id)
    if (!force && cachedPerson && isCacheValid.value) {
      selectedPerson.value = cachedPerson
      return cachedPerson
    }

    setLoading(true)
    clearError()

    try {
      const person = await peopleService.getById(id)
      
      // Update the person in the people array if it exists
      const existingIndex = people.value.findIndex(p => p.id === id)
      if (existingIndex !== -1) {
        people.value[existingIndex] = person
      } else {
        // Add to people array if not exists
        people.value.push(person)
      }
      
      selectedPerson.value = person
      lastFetch.value = new Date().getTime()
      return person
    } catch (err) {
      console.error('Error fetching person:', err)
      setError(err.response?.data?.message || 'Failed to load person')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Create new person
  const createPerson = async (personData) => {
    setLoading(true)
    clearError()

    try {
      const newPerson = await peopleService.create(personData)
      people.value.unshift(newPerson) // Add to beginning of array
      selectedPerson.value = newPerson
      return newPerson
    } catch (err) {
      console.error('Error creating person:', err)
      setError(err.response?.data?.message || 'Failed to create person')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Update person
  const updatePerson = async (id, personData) => {
    setLoading(true)
    clearError()

    try {
      const updatedPerson = await peopleService.update(id, personData)
      
      // Update in people array
      const index = people.value.findIndex(p => p.id === id)
      if (index !== -1) {
        people.value[index] = updatedPerson
      }
      
      // Update selected person if it's the same one
      if (selectedPerson.value?.id === id) {
        selectedPerson.value = updatedPerson
      }
      
      return updatedPerson
    } catch (err) {
      console.error('Error updating person:', err)
      setError(err.response?.data?.message || 'Failed to update person')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Partial update person
  const patchPerson = async (id, personData) => {
    setLoading(true)
    clearError()

    try {
      const updatedPerson = await peopleService.partialUpdate(id, personData)
      
      // Update in people array
      const index = people.value.findIndex(p => p.id === id)
      if (index !== -1) {
        people.value[index] = updatedPerson
      }
      
      // Update selected person if it's the same one
      if (selectedPerson.value?.id === id) {
        selectedPerson.value = updatedPerson
      }
      
      return updatedPerson
    } catch (err) {
      console.error('Error updating person:', err)
      setError(err.response?.data?.message || 'Failed to update person')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Delete person
  const deletePerson = async (id) => {
    setLoading(true)
    clearError()

    try {
      await peopleService.delete(id)
      
      // Remove from people array
      people.value = people.value.filter(p => p.id !== id)
      
      // Clear selected person if it was the deleted one
      if (selectedPerson.value?.id === id) {
        selectedPerson.value = null
      }
      
      return true
    } catch (err) {
      console.error('Error deleting person:', err)
      setError(err.response?.data?.message || 'Failed to delete person')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // Clear selected person
  const clearSelectedPerson = () => {
    selectedPerson.value = null
  }

  // Force refresh cache
  const refreshCache = async () => {
    return await fetchPeople(true)
  }

  // Clear all data (useful for logout)
  const clearStore = () => {
    people.value = []
    selectedPerson.value = null
    error.value = null
    loading.value = false
    lastFetch.value = null
  }

  return {
    // State
    people,
    loading,
    error,
    selectedPerson,
    
    // Getters
    isLoading,
    hasError,
    peopleCount,
    getPeopleList,
    getPersonById,
    isCacheValid,
    
    // Actions
    clearError,
    fetchPeople,
    fetchPersonById,
    createPerson,
    updatePerson,
    patchPerson,
    deletePerson,
    clearSelectedPerson,
    refreshCache,
    clearStore
  }
})