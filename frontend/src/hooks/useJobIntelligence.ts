import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import { JobIntelligenceResponse } from '../types/resume'

export function useJobIntelligence() {
  return useQuery<JobIntelligenceResponse[]>({
    queryKey: ['job-intelligence'],
    queryFn: async () => {
      const response = await api.get('/job-description')
      return response.data
    },
  })
}

export function useExtractJobIntelligence() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (jobDescription: string) => {
      const response = await api.post('/job-description/extract', {
        job_description: jobDescription,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-intelligence'] })
    },
  })
}
