import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useResume, useUpdateResume, useRenameResume } from '../hooks/useResume'
import { Resume } from '../types/resume'
import { UnifiedResumeEditor } from '../components/UnifiedResumeEditor'
import { JobDescriptionSidebar } from '../components/JobDescriptionSidebar'
import axios from 'axios'

export default function Editor() {
  const { resumeId } = useParams<{ resumeId: string }>()
  const { data: resume, isLoading } = useResume(resumeId!)
  const updateResume = useUpdateResume()
  const renameResume = useRenameResume()

  const [editedResume, setEditedResume] = useState<Resume | null>(null)
  const [isRenamingResume, setIsRenamingResume] = useState(false)
  const [resumeName, setResumeName] = useState('')
  const [showJobSidebar, setShowJobSidebar] = useState(true)
  const [jobDescription, setJobDescription] = useState('')
  const [isOptimizing, setIsOptimizing] = useState(false)

  // Initialize edited resume
  useEffect(() => {
    if (resume) {
      setEditedResume(resume.data)
      setResumeName(resume.name)
    }
  }, [resume])

  // --- Actions ---

  const handleRename = async () => {
    if (!resumeId || !resumeName.trim()) return
    try {
      await renameResume.mutateAsync({ resumeId, name: resumeName })
      setIsRenamingResume(false)
    } catch (error) {
      console.error('Failed to rename resume:', error)
    }
  }

  const handleSave = async () => {
    if (!editedResume || !resumeId) return
    await updateResume.mutateAsync({
      resumeId,
      data: editedResume,
    })
  }

  const handleExport = async () => {
    if (!resumeId) return
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
      const response = await fetch(`${apiUrl}/export/pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          resume_id: resumeId,
          format: 'pdf',
          options: { theme: 'professional' }
        })
      })

      if (!response.ok) throw new Error('Export failed')

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${resume?.name || 'resume'}_optimized.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    } catch (error) {
      alert('Failed to export PDF')
    }
  }

  // --- Optimization ---

  const handleFullOptimization = async () => {
    if (!editedResume || !jobDescription) {
      alert('Please add a job description first!')
      setShowJobSidebar(true)
      return
    }

    setIsOptimizing(true)
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
      const token = await (async () => {
        // Get Firebase token
        const { auth } = await import('../config/firebase')
        const user = auth.currentUser
        return user ? await user.getIdToken() : null
      })()

      const response = await axios.post(`${apiUrl}/optimize/resume`, {
        resume_data: editedResume,
        job_description: jobDescription
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      const optimizations = response.data // Map of original -> optimized

      // Store optimized bullets for diff highlighting
      // const newOptimizedMap = new Map<string, string>()
      // Object.entries(optimizations).forEach(([original, optimized]) => {
      //   newOptimizedMap.set(original, optimized as string)
      // })
      // setOptimizedBullets(newOptimizedMap)

      // Apply optimizations to resume state
      const newResume = { ...editedResume }
      let changeCount = 0

      newResume.experience.forEach(exp => {
        exp.bullets = exp.bullets.map(bullet => {
          if (optimizations[bullet]) {
            changeCount++
            return optimizations[bullet] as string // Replace with optimized version
          }
          return bullet
        })
      })

      // Also optimize project bullets
      newResume.projects?.forEach(proj => {
        proj.bullets = proj.bullets.map(bullet => {
          if (optimizations[bullet]) {
            changeCount++
            return optimizations[bullet] as string
          }
          return bullet
        })
      })

      setEditedResume(newResume)
      alert(`Optimization complete! Updated ${changeCount} bullets. Changes are highlighted in yellow.`)

    } catch (error: any) {
      console.error('Full optimization failed:', error)
      const errorMessage = error?.response?.data?.detail || error?.message || 'Optimization failed. Please try again.'
      alert(errorMessage)
    } finally {
      setIsOptimizing(false)
    }
  }

  // --- State Updates ---

  // --- State Updates ---

  // TODO: Implement HTML-to-JSON parsing to update structured data from editor content
  // Currently, edits in the WYSIWYG editor are not reflected in the structured Resume object
  // which is what gets saved to the backend.

  /* Unused helper functions - kept for reference if we add structured editing back
  const updateExperience = (idx: number, field: keyof ExperienceItem, value: any) => {
    if (!editedResume) return
    const newExp = [...editedResume.experience]
    newExp[idx] = { ...newExp[idx], [field]: value }
    setEditedResume({ ...editedResume, experience: newExp })
  }

  const updateBullet = (expIdx: number, bulletIdx: number, value: string) => {
    if (!editedResume) return
    const newExp = [...editedResume.experience]
    newExp[expIdx].bullets[bulletIdx] = value
    setEditedResume({ ...editedResume, experience: newExp })
  }

  const addBullet = (expIdx: number) => {
    if (!editedResume) return
    const newExp = [...editedResume.experience]
    newExp[expIdx].bullets.push('')
    setEditedResume({ ...editedResume, experience: newExp })
  }

  const removeBullet = (expIdx: number, bulletIdx: number) => {
    if (!editedResume) return
    const newExp = [...editedResume.experience]
    newExp[expIdx].bullets = newExp[expIdx].bullets.filter((_, i) => i !== bulletIdx)
    setEditedResume({ ...editedResume, experience: newExp })
  }
  */

  if (isLoading || !editedResume) return <div className="p-8 text-center">Loading...</div>

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Navbar */}
      <nav className="bg-white shadow-sm border-b border-gray-200 z-20 sticky top-0">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-4">
              <Link to="/dashboard" className="text-xl font-bold text-gray-900">ResuMAX</Link>
              <div className="h-6 w-px bg-gray-300"></div>
              {isRenamingResume ? (
                <input
                  type="text"
                  value={resumeName}
                  onChange={(e) => setResumeName(e.target.value)}
                  onBlur={handleRename}
                  onKeyDown={(e) => e.key === 'Enter' && handleRename()}
                  autoFocus
                  className="px-2 py-1 border rounded"
                />
              ) : (
                <button onClick={() => setIsRenamingResume(true)} className="font-medium hover:text-blue-600">
                  {resumeName}
                </button>
              )}
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowJobSidebar(!showJobSidebar)}
                className={`px-3 py-1.5 text-sm font-medium rounded-md border ${showJobSidebar ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-white border-gray-300 text-gray-700'
                  }`}
              >
                {showJobSidebar ? 'Hide Job' : 'Add Job Description'}
              </button>

              <button
                onClick={handleFullOptimization}
                disabled={isOptimizing}
                className="px-3 py-1.5 text-sm font-medium bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 shadow-sm"
              >
                {isOptimizing ? '✨ Optimizing...' : '✨ Auto-Optimize'}
              </button>

              <div className="h-6 w-px bg-gray-300 mx-2"></div>

              <button onClick={handleSave} className="text-sm font-medium text-gray-600 hover:text-gray-900">
                Save
              </button>
              <button onClick={handleExport} className="px-3 py-1.5 text-sm font-medium bg-green-600 text-white rounded-md hover:bg-green-700 shadow-sm">
                Export PDF
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">

        {/* Document Editor (Centered) */}
        <div className="flex-1 overflow-y-auto p-8 bg-gray-100 flex justify-center">
          {editedResume && (
            <UnifiedResumeEditor
              resume={editedResume}
              onChange={(html) => {
                // For now, just save the HTML - we'll parse it back to structured data when needed
                console.log('Resume HTML changed:', html);
              }}
            />
          )}
        </div>

        {/* Job Sidebar (Right) */}
        {showJobSidebar && (
          <div className="w-96 border-l border-gray-200 bg-white shadow-xl z-10 flex flex-col">
            <JobDescriptionSidebar
              resumeId={resumeId}
              onKeywordsExtracted={(keywords) => console.log(keywords)}
              jobDescription={jobDescription}
              onJobDescriptionChange={setJobDescription}
            />
          </div>
        )}
      </div>
    </div>
  )
}
