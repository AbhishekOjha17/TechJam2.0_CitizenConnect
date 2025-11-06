'use client' 
import React from 'react'
import Link from 'next/link'
function Header() {
  return (
    <div>
      <div className='container mx-auto' >
        <div className='xl:w-[1200px] text-lg mx-auto flex items-center justify-between p-10 py-7' >
         
            <Link href="/">  <h1 className='font-bold polysans text-2xl' > Citizen Connect </h1></Link> 


         
          <div className='flex gap-5 text-[16px]'>

            <Link href="/"> <h2 className='cursor-pointer' >Home</h2> </Link> 
            <Link href="/registerComplaint" >

              <h2 className='cursor-pointer' >Register Complaint</h2>
            </Link>


            <Link href="/administrator" >

              <h2 className='cursor-pointer' >Administrator Login</h2>
            </Link>

          </div>
        </div>

      </div>

    </div>
  )
}

export default Header
