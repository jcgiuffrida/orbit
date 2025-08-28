import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: '/api/',
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
})

// Function to get CSRF token
export const getCsrfToken = async () => {
  try {
    const response = await api.get('auth/csrf/')
    return response.data.csrfToken
  } catch (error) {
    console.error('Error getting CSRF token:', error)
    return null
  }
}

// Request interceptor to include CSRF token
api.interceptors.request.use(
  async (config) => {
    // For POST, PUT, PATCH, DELETE requests, ensure we have CSRF token
    if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase())) {
      const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value
      if (token) {
        config.headers['X-CSRFToken'] = token
      } else {
        // If no token in DOM, get it from API
        const csrfToken = await getCsrfToken()
        if (csrfToken) {
          config.headers['X-CSRFToken'] = csrfToken
        }
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403 && error.response?.data?.detail === 'Authentication credentials were not provided.') {
      // Redirect to login or handle auth error
      console.log('Authentication required')
    }
    return Promise.reject(error)
  }
)

export default api