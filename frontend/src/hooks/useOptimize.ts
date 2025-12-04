import { useMutation } from '@tanstack/react-query'
import api from '../lib/api'

interface BulletOptimizationRequest {
  bullet: string
  context: {
    job_title?: string
    company?: string
    job_intelligence_id?: string
  }
}

interface BulletOptimizationResponse {
  original: string
  optimized: string
  reasoning?: string
  keywords_matched: string[]
}

interface SectionOptimizationRequest {
  section: string
  content: string
  context: {
    target_role?: string
    job_intelligence_id?: string
  }
}

interface SectionOptimizationResponse {
  section: string
  original: string
  optimized: string
  keywords_matched: string[]
  suggestions: string[]
}

export function useOptimizeBullet() {
  return useMutation<BulletOptimizationResponse, Error, BulletOptimizationRequest>({
    mutationFn: async (request) => {
      const response = await api.post('/optimize/bullet', request)
      return response.data
    },
  })
}

export function useOptimizeSection() {
  return useMutation<SectionOptimizationResponse, Error, SectionOptimizationRequest>({
    mutationFn: async (request) => {
      const response = await api.post('/optimize/section', request)
      return response.data
    },
  })
}
