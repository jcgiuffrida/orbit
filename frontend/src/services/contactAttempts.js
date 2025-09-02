import api from './api'

export const contactAttemptsService = {
  async fetchContactAttempts() {
    const response = await api.get('/pings/')
    return response.data.results
  },

  async fetchContactAttemptsForPerson(personId) {
    const response = await api.get(`/pings/?person=${personId}`)
    return response.data.results
  },

  async fetchContactAttemptById(id) {
    const response = await api.get(`/pings/${id}/`)
    return response.data
  },

  async createContactAttempt(contactAttemptData) {
    const response = await api.post('/pings/', contactAttemptData)
    return response.data
  },

  async updateContactAttempt(id, contactAttemptData) {
    const response = await api.put(`/pings/${id}/`, contactAttemptData)
    return response.data
  },

  async deleteContactAttempt(id) {
    await api.delete(`/pings/${id}/`)
  }
}

export const contactAttemptTypes = [
  { label: 'Text Message', value: 'text', icon: 'sms', color: 'info' },
  { label: 'Email', value: 'email', icon: 'email', color: 'secondary' },
  { label: 'Phone Call', value: 'call', icon: 'phone', color: 'positive' },
  { label: 'Social Media', value: 'social', icon: 'share', color: 'accent' },
  { label: 'Other', value: 'other', icon: 'contact_phone', color: 'grey-6' }
]

export const getContactAttemptTypeIcon = (type) => {
  const typeConfig = contactAttemptTypes.find(t => t.value === type)
  return typeConfig?.icon || 'contact_phone'
}

export const getContactAttemptTypeLabel = (type) => {
  const typeConfig = contactAttemptTypes.find(t => t.value === type)
  return typeConfig?.label || 'Other'
}

export const getContactAttemptTypeColor = (type) => {
  const typeConfig = contactAttemptTypes.find(t => t.value === type)
  return typeConfig?.color || 'grey-6'
}