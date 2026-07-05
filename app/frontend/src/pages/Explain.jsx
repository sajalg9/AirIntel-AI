import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, ResponsiveContainer } from 'recharts'
import { CitySelect, Spinner, ErrorBox, SectionHeader } from '../components/AQIUtils'

const API = '/api'
const COLORS = ['#00b4d8','#a78bfa','#fb7185','#fb923c','#34d399','#fbbf24']

export default function Explain() {
  const [city,    setCity]    = useState('Delhi')
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  async function fetchExplain(c) {
    setLoading(true); setError(null)
    try {
      const res = await axios.get(`${API}/explain/${c}`)
      setData(res.data)
    } catch(e) { setError(e.message) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchExplain(city) }, [city])

  const chartData = data
    ? Object.entries(data.contributions)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
    : []

  return (
    <div>
      <SectionHeader title="🔍 Source Attribution"
        sub="SHAP-based pollutant contribution to predicted AQI" />

      <div className="mb-6 rounded-3xl border border-slate-100 bg-white p-4 shadow-md">
        <CitySelect value={city} onChange={c => { setCity(c) }} />
      </div>

      {loading && <Spinner />}
      {error   && <ErrorBox msg={error} />}

      {!loading && data && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Summary card */}
          <div className="flex flex-col gap-4 rounded-3xl border border-slate-100 bg-white p-6 shadow-md">
            <h3 className="text-sm uppercase tracking-wider text-slate-500">Key Insight</h3>
            <p className="text-lg font-semibold leading-relaxed text-slate-900">
              {data.summary}
            </p>
            <div className="mt-auto">
              <p className="mb-2 text-xs text-slate-400">Dominant pollutant</p>
              <span className="rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-sm font-medium text-sky-600 shadow-sm">
                {data.dominant}
              </span>
            </div>
            
           
          </div>

          {/* Horizontal bar chart */}
          <div className="lg:col-span-2 rounded-3xl border border-slate-100 bg-white p-6 shadow-md" style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.08)' }}>
            <h3 className="mb-4 text-sm uppercase tracking-wider text-slate-500">Contribution (%)</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData} layout="vertical" margin={{left:10,right:30}}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false}/>
                <XAxis type="number" stroke="#94a3b8" tick={{fontSize:11}} domain={[0,100]}
                  tickFormatter={v => `${v}%`}/>
                <YAxis type="category" dataKey="name" stroke="#94a3b8" tick={{fontSize:12}} width={55}/>
                <Tooltip formatter={v => [`${v}%`, 'Contribution']} contentStyle={{background:'#ffffff',border:'1px solid #e2e8f0',borderRadius:'14px',color:'#0f172a'}}/>
                <Bar dataKey="value" radius={[0,6,6,0]}>
                  {chartData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]}/>
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>

            {/* Inline % badges */}
            <div className="flex flex-wrap gap-2 mt-4">
              {chartData.map((d, i) => (
                <span key={d.name}
                  className="text-xs px-3 py-1 rounded-full font-medium text-slate-700"
                  style={{background: COLORS[i % COLORS.length] + '33',
                          border: `1px solid ${COLORS[i % COLORS.length]}66`}}>
                  {d.name}: {d.value}%
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
