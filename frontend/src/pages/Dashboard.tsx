import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useResumes, useDeleteResume } from '../hooks/useResume'

export default function Dashboard() {
  const { user, signOut } = useAuth()
  const { data: resumes, isLoading } = useResumes()
  const deleteResume = useDeleteResume()
  const navigate = useNavigate()

  const handleSignOut = async () => {
    await signOut()
    navigate('/login')
  }

  const handleDelete = async (resumeId: string, resumeName: string, e: React.MouseEvent) => {
    e.preventDefault() // Prevent navigation to editor
    e.stopPropagation()

    if (window.confirm(`Are you sure you want to delete "${resumeName}"? This action cannot be undone.`)) {
      try {
        await deleteResume.mutateAsync(resumeId)
        // Success - query invalidation will update the UI
      } catch (error: any) {
        console.error('Failed to delete resume:', error)
        const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to delete resume. Please try again.'
        alert(errorMessage)
      }
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">ResuMAX</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">{user?.email}</span>
              <button
                onClick={handleSignOut}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="md:flex md:items-center md:justify-between mb-8">
          <div className="flex-1 min-w-0">
            <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
              My Resumes
            </h2>
          </div>
          <div className="mt-4 flex md:mt-0 md:ml-4">
            <Link
              to="/upload"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Upload Resume
            </Link>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="text-gray-500">Loading resumes...</div>
          </div>
        ) : resumes && resumes.length > 0 ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {resumes.map((resume) => (
              <div
                key={resume.resume_id}
                className="relative group"
              >
                <Link
                  to={`/editor/${resume.resume_id}`}
                  className="block p-6 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {resume.name}
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    {resume.data.header.name || 'No name'}
                  </p>
                  <div className="text-xs text-gray-500">
                    Updated {new Date(resume.updated_at).toLocaleDateString()}
                  </div>
                </Link>
                <button
                  onClick={(e) => handleDelete(resume.resume_id, resume.name, e)}
                  className="absolute top-4 right-4 p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Delete resume"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-gray-500 mb-4">No resumes yet</div>
            <Link
              to="/upload"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              Upload your first resume
            </Link>
          </div>
        )}
      </main>
    </div>
  )
}
