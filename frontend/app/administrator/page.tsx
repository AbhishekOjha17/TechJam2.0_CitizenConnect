'use client'

import { useState } from 'react'
import { setCookie, getCookie } from 'cookies-next'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const router = useRouter()

  // Redirect if already logged in
  if (typeof window !== 'undefined' && getCookie('isLoggedIn') === 'true') {
    router.push('/administrator/dashboard')
  }

  const handleLogin = (e: any) => {
    e.preventDefault()
    if (email && password) {
      setCookie('isLoggedIn', 'true', { maxAge: 3600 })
      router.push('/administrator/dashboard')
    } else {
      alert('Enter credentials')
    }
  }

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <form
        onSubmit={handleLogin}
        className="bg-white shadow-md rounded-xl p-8 w-full max-w-sm"
      >
        <h1 className="text-2xl font-semibold text-center mb-6">Officials Login</h1>
        <input
          type="email"
          placeholder="Email Address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border w-full mb-3 p-2 rounded-md"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border w-full mb-5 p-2 rounded-md"
        />
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
        >
          Login
        </button>
      </form>
    </div>
  )
}
