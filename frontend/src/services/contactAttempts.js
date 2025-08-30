import api from './api'

export const contactAttemptsService = {
  async fetchContactAttempts() {
    const response = await api.get('/contact-attempts/')
    return response.data.results
  },

  async fetchContactAttemptsForPerson(personId) {
    const response = await api.get(`/contact-attempts/?person=${personId}`)
    return response.data.results
  },

  async fetchContactAttemptById(id) {
    const response = await api.get(`/contact-attempts/${id}/`)
    return response.data
  },

  async createContactAttempt(contactAttemptData) {
    const response = await api.post('/contact-attempts/', contactAttemptData)
    return response.data
  },

  async updateContactAttempt(id, contactAttemptData) {
    const response = await api.put(`/contact-attempts/${id}/`, contactAttemptData)
    return response.data
  },

  async deleteContactAttempt(id) {
    await api.delete(`/contact-attempts/${id}/`)
  }
}

export const contactAttemptTypes = [
  { label: 'Text Message', value: 'text', icon: 'sms' },
  { label: 'Email', value: 'email', icon: 'email' },
  { label: 'Phone Call', value: 'call', icon: 'phone' },
  { label: 'Social Media', value: 'social', icon: 'share' },
  { label: 'Other', value: 'other', icon: 'contact_phone' }
]

export const getContactAttemptTypeIcon = (type) => {
  const typeConfig = contactAttemptTypes.find(t => t.value === type)
  return typeConfig?.icon || 'contact_phone'
}

export const getContactAttemptTypeLabel = (type) => {
  const typeConfig = contactAttemptTypes.find(t => t.value === type)
  return typeConfig?.label || 'Other'
}