'use client';

import React, { useEffect, useState } from 'react';
import { Star } from 'lucide-react';

function FeedbackPage() {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [anonymous, setAnonymous] = useState(true);
  const [service, setService] = useState('');
  const [city, setCity] = useState('');
  const [location, setLocation] = useState<{ lat?: number; lon?: number }>({});
  const [loadingLocation, setLoadingLocation] = useState(false);
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [imgFile, setImgFile] = useState<File | null>(null);

  const handleLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }

    setLoadingLocation(true);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation({
          lat: pos.coords.latitude,
          lon: pos.coords.longitude,
        });
        setLoadingLocation(false);
      },
      (err) => {
        console.warn('Location permission denied or error:', err.message);
        setLocation({});
        setLoadingLocation(false);
      }
    );
  };

  useEffect(() => {
    handleLocation();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  // build the report object according to backend model
  const reportData = {
    city,
    timestamp: new Date().toISOString(),
    rating,
    comment: (e.target as any).comment.value,
    public_service: service,
    district: city,
    device_location: location.lat && location.lon ? `${location.lat},${location.lon}` : undefined,
    is_anonymous: anonymous,
    name: anonymous ? undefined : name,
    gender: anonymous ? undefined : gender,
    age: anonymous ? undefined : age,
    imgDesc: "User uploaded image related to the issue", // ✅ optional
    imgSeverity: 3, // ✅ optional severity level (1–5)
    imgTag: ["feedback", "issue"], // optional tags if you want
  };

  const formData = new FormData();
  formData.append("report", JSON.stringify(reportData)); // ✅ single JSON string
  if (imgFile) formData.append("imgFile", imgFile); // ✅ optional image

  try {
    const res = await fetch("http://127.0.0.1:8000/report", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) throw new Error(`Error: ${res.status}`);
    const data = await res.json();
    console.log("✅ Submitted feedback:", data);
    alert("Feedback submitted successfully!");
  } catch (err) {
    console.error("❌ Submission failed:", err);
    alert("Error submitting feedback.");
  }
};


  return (
    <div className="xl:w-[1200px] mx-auto px-4 relative">
      {loadingLocation && (
        <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-white/80 backdrop-blur-sm">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-700 font-medium">Detecting your location...</p>
        </div>
      )}

      <h1 className="py-6 text-3xl text-center font-bold polysans">
        Fill in details of your complaint.
      </h1>

      <div className="my-2">
        <div className="lg:w-[600px] mx-auto bg-white p-6 rounded-2xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Service */}
            <div className="space-y-2">
              <label htmlFor="service" className="font-medium">
                Select Service
              </label>
              <select
                id="service"
                name="service"
                value={service}
                onChange={(e) => setService(e.target.value)}
                className="w-full rounded-md border border-gray-300 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Choose a service...</option>
                <option value="Water Supply">Water Supply</option>
                <option value="Electricity">Electricity</option>
                <option value="Waste Management">Waste Management</option>
                <option value="Road Maintenance">Road Maintenance</option>
                <option value="Traffic Management">Traffic Management</option>
                <option value="Garbage Collection">Garbage Collection</option>
                <option value="Public Transport">Public Transport</option>
                <option value="Street Lights">Street Lights</option>
              </select>
            </div>

            {/* City */}
            <div className="space-y-2">
              <label htmlFor="city" className="font-medium">
                Select City / District
              </label>
              <select
                id="city"
                name="city"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full rounded-md border border-gray-300 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Choose a city...</option>
                <option value="Delhi">Delhi</option>
                <option value="Mumbai">Mumbai</option>
                <option value="Chennai">Chennai</option>
                <option value="Bengaluru">Bengaluru</option>
                <option value="Kolkata">Kolkata</option>
                <option value="Pune">Pune</option>
                <option value="Hyderabad">Hyderabad</option>
                <option value="Ahmedabad">Ahmedabad</option>
              </select>

              {location.lat && (
                <p className="text-sm text-green-600">
                  ✅ Location captured: {location.lat.toFixed(4)}, {location.lon?.toFixed(4)}
                </p>
              )}
            </div>

            {/* Rating */}
            <div className="space-y-2">
              <label className="font-medium">Rating</label>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`h-6 w-6 cursor-pointer ${
                      (hover || rating) >= star ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                    }`}
                    onMouseEnter={() => setHover(star)}
                    onMouseLeave={() => setHover(0)}
                    onClick={() => setRating(star)}
                  />
                ))}
              </div>
            </div>

            {/* Feedback */}
            <div className="space-y-2">
              <label htmlFor="comment" className="font-medium">
                Share your feedback
              </label>
              <textarea
                id="comment"
                name="comment"
                placeholder="Describe your experience or concern..."
                required
                className="w-full rounded-md border border-gray-300 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[100px]"
              />
            </div>

            {/* Upload Image */}
            <div className="space-y-2">
              <label htmlFor="imgFile" className="font-medium">
                Upload Image
              </label>
              <input
                id="imgFile"
                name="imgFile"
                type="file"
                accept="image/*"
                onChange={(e) => setImgFile(e.target.files?.[0] || null)}
                className="cursor-pointer w-full border border-gray-300 rounded-md p-2"
              />
            </div>

            {/* Anonymous */}
            <div className="space-y-2">
              <label className="font-medium">Do you want to stay anonymous?</label>
              <div className="flex gap-6">
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="anonymous"
                    value="yes"
                    checked={anonymous}
                    onChange={() => setAnonymous(true)}
                  />
                  Yes
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="anonymous"
                    value="no"
                    checked={!anonymous}
                    onChange={() => setAnonymous(false)}
                  />
                  No
                </label>
              </div>
            </div>

            {/* Show Name, Age, Gender if Not Anonymous */}
            {!anonymous && (
              <div className="space-y-4 border-t border-gray-200 pt-4">
                <div className="space-y-2">
                  <label htmlFor="name" className="font-medium">
                    Name
                  </label>
                  <input
                    id="name"
                    name="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your name"
                    required
                    className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="space-y-2">
                  <label htmlFor="age" className="font-medium">
                    Age
                  </label>
                  <input
                    id="age"
                    name="age"
                    type="number"
                    min="1"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    placeholder="Enter your age"
                    required
                    className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="space-y-2">
                  <label htmlFor="gender" className="font-medium">
                    Gender
                  </label>
                  <select
                    id="gender"
                    name="gender"
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    required
                    className="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select gender...</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition"
            >
              Submit Feedback
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default FeedbackPage;
