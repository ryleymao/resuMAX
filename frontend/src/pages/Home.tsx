import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full bg-white rounded-2xl shadow-xl p-12">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-gray-900 mb-4">
            Resu<span className="text-blue-600">MAX</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Optimize your resume instantly with AI-powered matching
          </p>

          <div className="flex gap-4 justify-center mb-12">
            <Link
              to="/login"
              className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-md"
            >
              Login
            </Link>
            <Link
              to="/signup"
              className="px-8 py-3 bg-white text-blue-600 border-2 border-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
            >
              Sign Up
            </Link>
          </div>

          <div className="grid md:grid-cols-3 gap-6 text-left">
            <div className="p-6 bg-blue-50 rounded-lg">
              <div className="text-3xl mb-2">📄</div>
              <h3 className="font-bold text-lg mb-2">Upload Resume</h3>
              <p className="text-gray-600 text-sm">
                Upload your resume and let our AI parse all your experience automatically
              </p>
            </div>
            <div className="p-6 bg-indigo-50 rounded-lg">
              <div className="text-3xl mb-2">✨</div>
              <h3 className="font-bold text-lg mb-2">Optimize Instantly</h3>
              <p className="text-gray-600 text-sm">
                Paste a job description and get AI-optimized bullet points in seconds
              </p>
            </div>
            <div className="p-6 bg-purple-50 rounded-lg">
              <div className="text-3xl mb-2">✏️</div>
              <h3 className="font-bold text-lg mb-2">Edit & Export</h3>
              <p className="text-gray-600 text-sm">
                Edit your resume in a rich text editor and export to PDF when ready
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
