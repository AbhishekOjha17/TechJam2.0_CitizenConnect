'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { getCookie } from 'cookies-next'
import { useEffect } from 'react'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  // Redirect to login if not logged in
  useEffect(() => {
    if (getCookie('isLoggedIn') !== 'true') router.push('/')
  }, [router])

  return (
    <div className="  flex">
      {/* Sidebar */}
      
      <aside className="pt-30 w-40 h-[100vh] fixed top-0  bg-[#e4e4e4] text-black flex flex-col p-5 space-y-1 pb-4"> 
        <Link href="/administrator/dashboard" className="hover:bg-[#d7d7d7] p-2 px-4 rounded-4xl">Dashboard</Link>
        <Link href="/administrator/dashboard/services" className="hover:bg-[#d7d7d7] p-2 px-4 rounded-4xl">Services</Link>
        <Link href="/administrator/dashboard/settings" className="hover:bg-[#d7d7d7] p-2 px-4 rounded-4xl">Settings</Link>
        <Link href="/administrator/dashboard/logout" className="mt-auto text-white bg-red-600 hover:bg-red-700 p-2 rounded-4xl text-center">
          Logout
        </Link>
      </aside>

      {/* Main content */}
      <main className=" ml-40 flex-1 p-6 bg-gray-50">{children}</main>
    </div>
  )
}
