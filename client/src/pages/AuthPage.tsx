import { useState } from 'react'
import SignIn from '../components/auth/SignIn'
import SignUp from '../components/auth/SignUp'

export default function AuthPage() {
  const [tab, setTab] = useState<'signin' | 'signup'>('signin')

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <p className="text-2xl font-semibold text-gray-900">FloorMan</p>
          <p className="text-sm text-gray-500 mt-1">Sign in to access your knowledge base</p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          {/* Tabs */}
          <div className="flex bg-gray-100 rounded-lg p-1 mb-6">
            <button
              onClick={() => setTab('signin')}
              className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-colors ${
                tab === 'signin'
                  ? 'bg-white text-gray-900 shadow-xs'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setTab('signup')}
              className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-colors ${
                tab === 'signup'
                  ? 'bg-white text-gray-900 shadow-xs'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Sign Up
            </button>
          </div>

          {tab === 'signin' ? <SignIn /> : <SignUp />}
        </div>
      </div>
    </div>
  )
}
