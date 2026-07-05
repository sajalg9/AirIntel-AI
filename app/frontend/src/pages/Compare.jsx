import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Spinner, ErrorBox, SectionHeader, getAQILevel } from '../components/AQIUtils'
import { apiUrl } from '../lib/api'
const CITIES = ['Delhi', 'Mumbai', 'Bangalore', 'Hyderabad', 'Chennai']

export default function Compare() {
  const [selected, setSelected] = useState(new Set(CITIES))
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  function toggle(city) {
    setSelected(prev => {
      const next = new Set(prev)
      next.has(city) ? next.delete(city) : next.add(city)
      return next
    })
  }

  async function fetchCompare() {
    if (selected.size === 0) return
    setLoading(true)
    setError(null)
    try {
      const res = await axios.get(apiUrl(`/compare?cities=${[...selected].join(',')}`))
      setData(res.data.comparison)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCompare()
  }, [selected])

  const chartData = data?.map(d => ({
    city: d.city,
    Current: d.current_aqi,
    'Day +1': d.forecast_day1,
    'Day +2': d.forecast_day2,
    'Day +3': d.forecast_day3,
  })) ?? []

  const barSize =
    chartData.length <= 2 ? 45 :
      chartData.length === 3 ? 32 :
        chartData.length === 4 ? 22 :
          18

  const categoryGap =
    chartData.length <= 2 ? '45%' :
      chartData.length === 3 ? '30%' :
        '18%'

  return (
    <div>
      <SectionHeader
        title="🏙️ City Comparison"
        sub="Current and forecasted AQI across multiple Indian cities"
      />

      <div className="mb-8 flex flex-wrap gap-3 rounded-3xl border border-slate-100 bg-white p-4 shadow-md">
        {CITIES.map(city => (
          <button
            key={city}
            onClick={() => toggle(city)}
            className={`rounded-full border px-6 py-2 font-semibold transition-all ${selected.has(city)
                ? 'bg-sky-500 border-sky-500 text-white shadow-sm'
                : 'bg-white border-slate-200 text-slate-600 hover:border-slate-400'
              }`}
          >
            {city}
          </button>
        ))}
      </div>

      {loading && <Spinner />}
      {error && <ErrorBox msg={error} />}

      {!loading && chartData.length > 0 && (
        <>
          <div className="mb-6 rounded-3xl border border-slate-100 bg-white p-8 shadow-md" style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.08)' }}>
            <ResponsiveContainer width="100%" height={430}>
              <BarChart
                data={chartData}
                barSize={barSize}
                barCategoryGap={categoryGap}
                margin={{ top: 20, right: 30, left: 10, bottom: 40 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="city" stroke="#94a3b8" interval={0} height={50} tick={{ fontSize: 16 }} />
                <YAxis stroke="#94a3b8" domain={[0, 'auto']} />
                <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '14px', color: '#0f172a' }} />
                <Legend />
                <Bar dataKey="Current" fill="#0ea5e9" radius={[6, 6, 0, 0]} />
                <Bar dataKey="Day +1" fill="#a78bfa" radius={[6, 6, 0, 0]} />
                <Bar dataKey="Day +2" fill="#fb7185" radius={[6, 6, 0, 0]} />
                <Bar dataKey="Day +3" fill="#fb923c" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="overflow-x-auto rounded-3xl border border-slate-100 bg-white p-6 shadow-md">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left text-slate-500">
                  <th className="pb-3">City</th>
                  <th className="pb-3">Current AQI</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Day +1</th>
                  <th className="pb-3">Day +2</th>
                  <th className="pb-3">Day +3</th>
                </tr>
              </thead>
              <tbody>
                {data.map(d => {

  const getBadge = (category) => {

    if(category === "Good")
      return "bg-green-500"

    if(category === "Satisfactory")
      return "bg-emerald-500"

    if(category === "Moderate")
      return "bg-yellow-500"

    if(category === "Poor")
      return "bg-orange-500"

    if(category === "Very Poor")
      return "bg-red-500"

    return "bg-purple-600"
  }


  const lvl = getAQILevel(d.current_aqi)


  return (

    <tr 
      key={d.city}
      className="border-b border-slate-300"
    >


      <td className="
        py-4
        font-bold
        text-slate-900
      ">
        {d.city}
      </td>



      <td
        className={`
        py-4
        text-xl
        font-black
        ${lvl.text}
        `}
      >

        {d.current_aqi}

      </td>




      <td>

        <span

          className={`
          inline-flex
          min-w-[120px]
          justify-center
          rounded-full
          px-4
          py-2

          text-xs
          font-black
          uppercase
          tracking-wider

          text-white
          shadow-lg

          ${getBadge(d.category)}
          `}

        >

          {d.category}

        </span>


      </td>




      <td className="text-purple-500 font-semibold">

        {d.forecast_day1}

      </td>



      <td className="text-pink-500 font-semibold">

        {d.forecast_day2}

      </td>



      <td className="text-orange-500 font-semibold">

        {d.forecast_day3}

      </td>


    </tr>


  )

})}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}