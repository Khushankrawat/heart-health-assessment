import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 500) {
      console.error('Server error:', error.response.data)
    }
    return Promise.reject(error)
  }
)

export interface HeartDiseaseInput {
  age: number
  gender: 'Male' | 'Female'
  cholesterol: number
  blood_pressure: number
  heart_rate: number
  smoking: 'Never' | 'Former' | 'Current'
  alcohol_intake: 'None' | 'Moderate' | 'Heavy'
  exercise_hours: number
  family_history: boolean
  diabetes: boolean
  obesity: boolean
  stress_level: number
  blood_sugar: number
  exercise_induced_angina: boolean
  chest_pain_type: 'Typical Angina' | 'Atypical Angina' | 'Non-anginal Pain' | 'Asymptomatic'
}

export interface FeatureContribution {
  feature: string
  value: number | string | boolean
  importance: number
}

export interface HeartDiseasePrediction {
  risk_score: number
  risk_level: 'Low' | 'Moderate' | 'High'
  top_contributors: FeatureContribution[]
  model_version: string
  notes: string[]
}

export interface UploadResponse {
  success: boolean
  message: string
  extracted_data?: HeartDiseaseInput
  confidence?: number
}

export const apiClient = {
  // Predict heart disease risk
  async predict(inputData: HeartDiseaseInput): Promise<HeartDiseasePrediction> {
    const response = await api.post('/predict', inputData)
    return response.data
  },

  // Upload health report
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Upload image specifically
  async uploadImage(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Get model info
  async getModelInfo() {
    const response = await api.get('/model-info')
    return response.data
  },

  // Health check
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  },

  // Get supported formats
  async getSupportedFormats() {
    const response = await api.get('/supported-formats')
    return response.data
  },
}

export default apiClient
