import apiClient from './api'

const relationshipsService = {
  // Get all relationships
  async getAll() {
    const response = await apiClient.get('relationships/')
    return response.data
  },

  // Get relationships for a specific person
  async getByPerson(personId) {
    const response = await apiClient.get('relationships/')
    const allRelationships = response.data.results || response.data
    
    // Filter relationships where the person is either person1 or person2
    return allRelationships.filter(rel => 
      rel.person1 === personId || rel.person2 === personId
    )
  },

  // Get a specific relationship by ID
  async getById(id) {
    const response = await apiClient.get(`relationships/${id}/`)
    return response.data
  },

  // Create a new relationship
  async create(relationshipData) {
    const response = await apiClient.post('relationships/', relationshipData)
    return response.data
  },

  // Update a relationship
  async update(id, relationshipData) {
    const response = await apiClient.put(`relationships/${id}/`, relationshipData)
    return response.data
  },

  // Partially update a relationship
  async partialUpdate(id, relationshipData) {
    const response = await apiClient.patch(`relationships/${id}/`, relationshipData)
    return response.data
  },

  // Delete a relationship
  async delete(id) {
    await apiClient.delete(`relationships/${id}/`)
    return true
  },

  // Get available relationship types
  getRelationshipTypes() {
    return [
      { label: 'Partner', value: 'partner' },
      { label: 'Family', value: 'family' },
      { label: 'Friend', value: 'friend' },
      { label: 'Colleague', value: 'colleague' },
      { label: 'Acquaintance', value: 'acquaintance' },
      { label: 'Other', value: 'other' }
    ]
  }
}

export default relationshipsService