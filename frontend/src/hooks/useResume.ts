import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import { ResumeResponse, Resume } from '../types/resume'

export function useResumes() {
  return useQuery<ResumeResponse[]>({
    queryKey: ['resumes'],
    queryFn: async () => {
      const response = await api.get('/resume')
      return response.data
    },
  })
}

export function useResume(resumeId: string) {
  return useQuery<ResumeResponse>({
    queryKey: ['resume', resumeId],
    queryFn: async () => {
      const response = await api.get(`/resume/${resumeId}`)
      return response.data
    },
    enabled: !!resumeId,
  })
}

export function useUpdateResume() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      resumeId,
      data,
      name,
    }: {
      resumeId: string
      data?: Partial<Resume>
      name?: string
    }) => {
      const payload: any = {}
      if (data !== undefined) payload.data = data
      if (name !== undefined) payload.name = name

      const response = await api.put(`/resume/${resumeId}`, payload)
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['resume', data.resume_id] })
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
    },
  })
}

export function useRenameResume() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      resumeId,
      name,
    }: {
      resumeId: string
      name: string
    }) => {
      const response = await api.put(`/resume/${resumeId}`, { name })
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['resume', data.resume_id] })
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
    },
  })
}

export function useUploadResume() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
    },
  })
}

export function useDeleteResume() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (resumeId: string) => {
      const response = await api.delete(`/resume/${resumeId}`)
      return response.data
    },
    onSuccess: (_, resumeId) => {
      // Remove from cache immediately
      queryClient.removeQueries({ queryKey: ['resume', resumeId] })
      // Invalidate list to refetch
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
    },
    onError: (error: any) => {
      console.error('Delete failed:', error)
      throw error
    },
  })
}
