import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import relationshipsService from '@/services/relationships'

export const useRelationshipsStore = defineStore('relationships', () => {
  const relationships = ref([])
  const isLoading = ref(false)
  const hasError = ref(false)
  const error = ref(null)
  const lastFetched = ref(null)

  // Very long cache duration since relationships rarely change
  const CACHE_DURATION = 30 * 60 * 1000 // 30 minutes

  const isCacheValid = computed(() => {
    if (!lastFetched.value) return false
    return (Date.now() - lastFetched.value) < CACHE_DURATION
  })

  const getRelationshipsList = computed(() => relationships.value)
  const relationshipsCount = computed(() => relationships.value.length)

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

  const fetchAllRelationships = async (forceRefresh = false) => {
    if (!forceRefresh && isCacheValid.value && relationships.value.length > 0) {
      return relationships.value
    }

    setLoading(true)
    clearError()

    try {
      const data = await relationshipsService.getAll()
      relationships.value = data.results || data
      lastFetched.value = Date.now()
      return relationships.value
    } catch (err) {
      console.error('Failed to fetch relationships:', err)
      setError('Failed to load relationships')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getRelationshipsForPerson = (personId) => {
    // Filter from cached relationships
    return relationships.value.filter(rel => 
      rel.person1 === personId || rel.person2 === personId
    )
  }

  const createRelationship = async (relationshipData) => {
    setLoading(true)
    clearError()

    try {
      const newRelationship = await relationshipsService.create(relationshipData)
      relationships.value.push(newRelationship)
      lastFetched.value = Date.now()
      return newRelationship
    } catch (err) {
      console.error('Failed to create relationship:', err)
      setError('Failed to create relationship')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const updateRelationship = async (id, relationshipData) => {
    setLoading(true)
    clearError()

    try {
      const updatedRelationship = await relationshipsService.update(id, relationshipData)
      
      const index = relationships.value.findIndex(r => r.id === id)
      if (index >= 0) {
        relationships.value[index] = updatedRelationship
      }
      
      return updatedRelationship
    } catch (err) {
      console.error('Failed to update relationship:', err)
      setError('Failed to update relationship')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const deleteRelationship = async (id) => {
    setLoading(true)
    clearError()

    try {
      await relationshipsService.delete(id)
      relationships.value = relationships.value.filter(r => r.id !== id)
    } catch (err) {
      console.error('Failed to delete relationship:', err)
      setError('Failed to delete relationship')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const invalidateCache = () => {
    lastFetched.value = null
  }

  return {
    relationships,
    isLoading,
    hasError,
    error,
    getRelationshipsList,
    relationshipsCount,
    isCacheValid,
    fetchAllRelationships,
    getRelationshipsForPerson,
    createRelationship,
    updateRelationship,
    deleteRelationship,
    invalidateCache
  }
})