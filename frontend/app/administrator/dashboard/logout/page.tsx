'use client'

import { deleteCookie } from 'cookies-next'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function LogoutPage() {
  const router = useRouter()

  useEffect(() => {
    deleteCookie('isLoggedIn')
    router.push('/')
  }, [router])

  return (
    <div className="flex items-center justify-center h-screen text-lg font-medium">
      Logging out...
    </div>
  )
}
