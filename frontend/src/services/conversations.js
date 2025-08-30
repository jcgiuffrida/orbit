import api from './api'

export const conversationsService = {
  async fetchConversations() {
    const response = await api.get('/conversations/')
    return response.data.results
  },

  async fetchConversationsForPerson(personId) {
    const response = await api.get(`/conversations/?participant=${personId}`)
    return response.data.results
  },

  async fetchConversationById(id) {
    const response = await api.get(`/conversations/${id}/`)
    return response.data
  },

  async createConversation(conversationData) {
    const response = await api.post('/conversations/', conversationData)
    return response.data
  },

  async updateConversation(id, conversationData) {
    const response = await api.put(`/conversations/${id}/`, conversationData)
    return response.data
  },

  async deleteConversation(id) {
    await api.delete(`/conversations/${id}/`)
  }
}

export const conversationTypes = [
  { label: 'In Person', value: 'in_person', icon: 'people' },
  { label: 'Phone Call', value: 'phone', icon: 'phone' },
  { label: 'Text Message', value: 'text', icon: 'sms' },
  { label: 'Email', value: 'email', icon: 'email' },
  { label: 'Video Call', value: 'video', icon: 'videocam' },
  { label: 'Other', value: 'other', icon: 'chat' }
]

export const getConversationTypeIcon = (type) => {
  const typeConfig = conversationTypes.find(t => t.value === type)
  return typeConfig?.icon || 'chat'
}

export const getConversationTypeLabel = (type) => {
  const typeConfig = conversationTypes.find(t => t.value === type)
  return typeConfig?.label || 'Other'
}