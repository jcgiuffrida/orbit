import api from './api'

export const peopleService = {
  // Get all people
  async getAll(params = {}) {
    try {
      const response = await api.get('people/', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get single person
  async getById(id) {
    try {
      const response = await api.get(`people/${id}/`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Create new person
  async create(personData) {
    try {
      const response = await api.post('people/', personData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Update person
  async update(id, personData) {
    try {
      const response = await api.put(`people/${id}/`, personData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Partial update person
  async partialUpdate(id, personData) {
    try {
      const response = await api.patch(`people/${id}/`, personData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Delete person
  async delete(id) {
    try {
      const response = await api.delete(`people/${id}/`)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default peopleService