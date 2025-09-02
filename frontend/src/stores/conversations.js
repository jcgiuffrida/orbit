import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { conversationsService } from '@/services/conversations'

export const useConversationsStore = defineStore('conversations', () => {
  const conversations = ref([])
  const selectedConversation = ref(null)
  const isLoading = ref(false)
  const hasError = ref(false)
  const error = ref(null)
  const lastFetched = ref(null)

  const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

  const isCacheValid = computed(() => {
    if (!lastFetched.value) return false
    return (Date.now() - lastFetched.value) < CACHE_DURATION
  })

  const getConversationsList = computed(() => conversations.value)
  const conversationsCount = computed(() => conversations.value.length)

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

  const fetchConversations = async (forceRefresh = false) => {
    if (!forceRefresh && isCacheValid.value && conversations.value.length > 0) {
      return conversations.value
    }

    setLoading(true)
    clearError()

    try {
      // First, get the first page
      const response = await conversationsService.fetchConversations()
      
      if (response.results) {
        let allConversations = [...response.results]
        
        // If there are more pages, fetch them all automatically
        let nextUrl = response.next
        while (nextUrl) {
          try {
            const nextUrlObj = new URL(nextUrl)
            const nextPage = nextUrlObj.searchParams.get('page')
            const nextResponse = await conversationsService.fetchConversations({ page: nextPage })
            
            if (nextResponse.results) {
              allConversations = [...allConversations, ...nextResponse.results]
              nextUrl = nextResponse.next
            } else {
              break
            }
          } catch (pageErr) {
            console.error('Error fetching additional conversation page:', pageErr)
            break
          }
        }
        
        conversations.value = allConversations
      } else {
        // Handle non-paginated response (fallback)
        conversations.value = response
      }
      
      lastFetched.value = Date.now()
      return conversations.value
    } catch (err) {
      console.error('Failed to fetch conversations:', err)
      setError('Failed to load conversations')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchConversationsForPerson = async (personId) => {
    setLoading(true)
    clearError()

    try {
      const data = await conversationsService.fetchConversationsForPerson(personId)
      return data
    } catch (err) {
      console.error('Failed to fetch conversations for person:', err)
      setError('Failed to load conversations')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchConversationById = async (id) => {
    setLoading(true)
    clearError()

    try {
      const data = await conversationsService.fetchConversationById(id)
      selectedConversation.value = data
      
      const existingIndex = conversations.value.findIndex(c => c.id === id)
      if (existingIndex >= 0) {
        conversations.value[existingIndex] = data
      }
      
      return data
    } catch (err) {
      console.error('Failed to fetch conversation:', err)
      setError('Failed to load conversation details')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const createConversation = async (conversationData) => {
    setLoading(true)
    clearError()

    try {
      const newConversation = await conversationsService.createConversation(conversationData)
      conversations.value.unshift(newConversation)
      lastFetched.value = Date.now()
      return newConversation
    } catch (err) {
      console.error('Failed to create conversation:', err)
      setError('Failed to create conversation')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const updateConversation = async (id, conversationData) => {
    setLoading(true)
    clearError()

    try {
      const updatedConversation = await conversationsService.updateConversation(id, conversationData)
      
      const index = conversations.value.findIndex(c => c.id === id)
      if (index >= 0) {
        conversations.value[index] = updatedConversation
      }
      
      if (selectedConversation.value?.id === id) {
        selectedConversation.value = updatedConversation
      }
      
      return updatedConversation
    } catch (err) {
      console.error('Failed to update conversation:', err)
      setError('Failed to update conversation')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const deleteConversation = async (id) => {
    setLoading(true)
    clearError()

    try {
      await conversationsService.deleteConversation(id)
      
      conversations.value = conversations.value.filter(c => c.id !== id)
      
      if (selectedConversation.value?.id === id) {
        selectedConversation.value = null
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err)
      setError('Failed to delete conversation')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const clearSelectedConversation = () => {
    selectedConversation.value = null
  }

  const invalidateCache = () => {
    lastFetched.value = null
  }

  return {
    conversations,
    selectedConversation,
    isLoading,
    hasError,
    error,
    getConversationsList,
    conversationsCount,
    isCacheValid,
    fetchConversations,
    fetchConversationsForPerson,
    fetchConversationById,
    createConversation,
    updateConversation,
    deleteConversation,
    clearSelectedConversation,
    invalidateCache
  }
})