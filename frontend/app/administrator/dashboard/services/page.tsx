'use client'

import React, { useState, useEffect } from 'react'
import { Bar, Pie } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Tooltip,
  Legend
)
import RatingCard from '@/components/RatingCard'

interface Stats {
  id: string
  scope: 'global' | 'district'
  district?: string | null

  avg_rating_overall: number
  avg_rating_by_service: Record<string, number>

  sentiment_counts_overall: {
    positive: number
    neutral: number
    negative: number
  }
  sentiment_counts_by_service: Record<
    string,
    {
      positive: number
      neutral: number
      negative: number
    }
  >

  total_feedback_overall: number
  total_feedback_by_service: Record<string, number>

  feedback_over_time: Record<string, number>
  last_updated: string
}

function Page() {
  const [analytics, setAnalytics] = useState<Stats | null>(null)
  const [barData, setBarData] = useState<any[]>([])
  
  const public_service = [
    "Water Supply",
    "Road Maintenance",
    "Electricity",
    "Traffic Management",
    "Garbage Collection",
    "Public Transport",
    "Street Lights",
  ]



  // ✅ 1️⃣ Fetch analytics first
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/analytics')
        const data: Stats = await res.json()
        setAnalytics(data)
      } catch (err) {
        console.error('Error fetching data:', err)
      }
    }


    const fetchDistrict = async () => {
      try {
        const res = await fetch("https://127.0.0.1:8000/analytics?scope=district&district=Chennai")
        const data: Stats = await res.json()
        setAnalytics(data)
      } catch (err) {
        console.log("teri mkc")
      }
    }

    fetchData()
  }, [])

  // ✅ 2️⃣ Build chart data *after* analytics is ready
  useEffect(() => {
    if (!analytics) return

    const bars = public_service.map((item) => {
      const serviceData = analytics.sentiment_counts_by_service[item] || {}
      return {
        labels: Object.keys(serviceData),
        datasets: [
          {
            label: item,
            data: Object.values(serviceData),
            backgroundColor: ['#16a34a', '#facc15', '#dc2626'],
          },
        ],
      }
    })

    setBarData(bars)
  }, [analytics]) // 🔥 runs only after analytics changes

  return (
    <div>
      <div>
         


        <h1 className='text-left font-medium my-4 text-2xl mt-3' >Ratings</h1>
        {analytics && (
          <div className='flex flex-wrap gap-4'>
            {public_service.map((item) => (
              <RatingCard
                key={item}
                title={item}
                rating={analytics.avg_rating_by_service[item]}
                totalFeedback={analytics.total_feedback_by_service[item]}
              />
            ))}
          </div>
        )}
      </div>

      <div>
        <h2 className='text-left font-medium mt-10 my-4 text-2xl mt-3' >Sentiments</h2>

        {barData.length > 0 && analytics && (
          <div className=' flex flex-wrap  gap-6'>
            {public_service.map((item, index) => (
              <div key={item} className="w-[240px] bg-white shadow rounded-xl p-4">
                <h2 className="text-lg font-medium mb-2">{item}</h2>
                {barData[index]?.labels?.length > 0 ? (
                  <Pie data={barData[index]} />
                ) : (
                  <p>No data</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Page
