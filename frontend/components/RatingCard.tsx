'use client'
import React from 'react'

interface RatingCardProps {
  title: string
  rating: number
  totalFeedback: number
}

export default function RatingCard({ title, rating, totalFeedback }: RatingCardProps) {
  const stars = 5
  const fullStars = Math.floor(rating)
  const hasHalfStar = rating % 1 >= 0.5
  const progressWidth = (rating / 5) * 100

  return (
    <div className="bg-white shadow-md rounded-2xl p-4 w-[200px] text-gray-800 flex justify-end flex-col items-start">
      {/* ⭐ Star Row */}
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
