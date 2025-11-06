'use client'

import { useEffect, useState } from 'react'
import { Bar, Pie, Line } from 'react-chartjs-2'
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


interface RatingCardProps {
  title: string
  rating: number
  totalFeedback: number
}

  function RatingCard({ title, rating, totalFeedback }: RatingCardProps) {
  const stars = 5
  const fullStars = Math.floor(rating)
  const hasHalfStar = rating % 1 >= 0.5
  const progressWidth = (rating / 5) * 100

  return (
    <div className="bg-white shadow-md rounded-2xl p-4 w-[200px] h-[100%] text-gray-800 flex  flex-col items-start">
      {/* ⭐ Star Row */}
                <h2 className="text-lg font-medium mb-2">Overall Rating</h2>

      <div className="flex items-center mb-2">
        {Array.from({ length: stars }).map((_, i) => {
          if (i < fullStars)
            return <span key={i} className="text-yellow-400 text-lg">★</span>
          if (i === fullStars && hasHalfStar)
            return <span key={i} className="text-yellow-400 text-lg">☆</span> // simple half look
          return <span key={i} className="text-gray-300 text-lg">★</span>
        })}
      </div>

      {/* Rating Number */}
      <div className="flex items-center mb-1">
        <span className="text-2xl font-bold">{rating.toFixed(1)}</span>
        <span className="ml-1 text-yellow-400">★</span>
      </div>

      {/* Feedback Count */}
      <p className="text-xs text-gray-500 mb-3">
        {totalFeedback} Feedback{totalFeedback !== 1 ? 's' : ''}
      </p>

      {/* Progress Bar */}
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-green-500 to-red-500"
          style={{ width: `${progressWidth}%` }}
        />
      </div>

      {/* Service Title */}
      <p className="mt-2 text-sm font-semibold text-gray-700">{title}</p>
    </div>
  )
}






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
    { positive: number; neutral: number; negative: number }
  >
  total_feedback_overall: number
  total_feedback_by_service: Record<string, number>
  feedback_over_time: Record<string, number>
  last_updated: string
}

interface Report {
  cleaned_comment?: string
  public_service?: string
  district?: string
}

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<Stats | null>(null)
  const [reports, setReports] = useState<Report[]>([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsRes, reportsRes] = await Promise.all([
          fetch('http://127.0.0.1:8000/analytics'),
          fetch('http://127.0.0.1:8000/reports/processed'),
        ])

        const analyticsData: Stats = await analyticsRes.json()
        const reportsData: Report[] = await reportsRes.json()

        setAnalytics(analyticsData)
        setReports(reportsData)
      } catch (err) {
        console.error('Error fetching data:', err)
      }
    }

    fetchData()
  }, [])

  const avgRating = analytics?.avg_rating_by_service ?? {}
  const sentiments = analytics?.sentiment_counts_overall ?? {}
  const feedbackTimeline = analytics?.feedback_over_time ?? {}

  const barData = {
    labels: Object.keys(avgRating),
    datasets: [
      {
        label: 'Average Rating',
        data: Object.values(avgRating),
        backgroundColor: '#2563eb',
      },
    ],
  }

  const pieData = {
    labels: Object.keys(sentiments),
    datasets: [
      {
        data: Object.values(sentiments),
        backgroundColor: ['#16a34a', '#facc15', '#dc2626'],
      },
    ],
  }

  const lineData = {
    labels: Object.keys(feedbackTimeline),
    datasets: [
      {
        label: 'Feedback Volume',
        data: Object.values(feedbackTimeline),
        borderColor: '#2563eb',
        tension: 0.4,
      },
    ],
  }

  return (
    <div className="space-y-10 p-6">
      <h1 className="text-2xl font-semibold mb-4">Welcome, Officer Sharma</h1>


      {/* ---- Charts ---- */}
      <div className="flex gap-4    ">

        <div className='flex gap-2 items-start  '>
          {analytics && (
            <RatingCard
              title="Overall" 
              rating={analytics.avg_rating_overall}
              totalFeedback={analytics.total_feedback_overall}
            />
          )}



        </div>


        <div className=" w-[450px]   bg-white shadow rounded-xl p-4">
          <h2 className="text-lg font-medium mb-2">Average Rating by Service</h2>
          {Object.keys(avgRating).length > 0 ? <Bar data={barData} /> : <p>No data</p>}
        </div>



        <div className="  bg-white shadow rounded-xl p-4">
          <h2 className="t ext-lg font-medium mb-2">Feedback Volume Over Time</h2>
          {Object.keys(feedbackTimeline).length > 0 ? <Line data={lineData} /> : <p>No data</p>}
        </div>
      </div>



      <div className='flex gap-2 items-start   '>
        {/* ---- Heatmap Section ---- */}
        <div className="w-[500px] h-[600px]  bg-white shadow rounded-xl p-4">
          <h2 className="text-lg font-medium mb-4">Geographical Heatmap</h2>
          <iframe
            src="http://127.0.0.1:8000/heatmap"
            className="w-full h-[500px] rounded-lg border border-gray-300"
            title="Heatmap Visualization"
          />
        </div>


        <div className=" w-[500px] h-[600px] bg-white shadow rounded-xl p-4">
          <h2 className="text-lg font-medium mb-4">Sentiment Distribution</h2>
          {Object.keys(sentiments).length > 0 ? <Pie data={pieData} /> : <p>No data</p>}
        </div>

      </div>


      {/* ---- Reports Table ---- */}
      <div className="bg-white shadow rounded-xl p-4">
        <h2 className="text-lg font-medium mb-4">Processed Reports</h2>
        {reports.length === 0 ? (
          <p>No processed reports yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full border border-gray-200 rounded-lg">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">
                    Cleaned Comment
                  </th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">
                    Department
                  </th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-600">
                    District
                  </th>
                </tr>
              </thead>
              <tbody>
                {reports.map((r, idx) => (
                  <tr key={idx} className="border-t hover:bg-gray-50 transition">
                    <td className="px-4 py-2 text-sm text-gray-800">
                      {r.cleaned_comment || 'N/A'}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-800">
                      {r.public_service || 'N/A'}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-800">
                      {r.district || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
