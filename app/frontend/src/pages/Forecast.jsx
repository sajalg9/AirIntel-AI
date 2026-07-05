import { useState, useEffect, useMemo } from 'react'
import axios from 'axios'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ReferenceLine, ResponsiveContainer, Brush
} from 'recharts'
import { CitySelect, Spinner, ErrorBox, SectionHeader, getAQILevel } from '../components/AQIUtils'
import { apiUrl } from '../lib/api'

const MODEL_OPTIONS = [
  { value: 'lstm', label: 'LSTM' },
  { value: 'transformer', label: 'Transformer' },
  { value: 'random_forest', label: 'Random Forest' },
]



function Card({ children, style }) {
  return (
    <div style={{
      background: '#fff', borderRadius: '14px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.07),0 4px 16px rgba(0,0,0,0.05)',
      ...style
    }}>{children}</div>
  )
}

export default function Forecast() {
  const [city, setCity] = useState('Delhi')
  const [model, setModel] = useState('lstm')
  const [model2, setModel2] = useState('transformer')
  const [days, setDays] = useState(7)
  const [data, setData] = useState(null)
  const [data2, setData2] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [brushRange, setBrushRange] = useState({
    startIndex: 0,
    endIndex: 60
  })

  async function fetchForecast() {
    setLoading(true); setError(null)
    try {
      const r1 = await axios.post(apiUrl('/forecast'), { city, days_ahead: days, model })
      setData(r1.data)
      try {
        const r2 = await axios.post(apiUrl('/forecast'), { city, days_ahead: days, model: model2 })
        setData2(r2.data)
      } catch { setData2(null) }
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchForecast() }, [city, model, model2, days])

  // Filter historical by selected range
  const filteredChartData = useMemo(() => {
    if (!data) return []

    let hist = [...data.historical]
      .sort((a, b) => new Date(a.date) - new Date(b.date))

    const chartData = hist.map(h => ({
      date: h.date,
      Historical: h.aqi,
      [model]: null,
      [model2]: null,
    }))

    data.forecast.forEach((f, i) => {
      chartData.push({
        date: `+${f.day}d`,
        Historical: null,
        [model]: f.predicted_aqi,
        [model2]: data2?.forecast[i]?.predicted_aqi ?? null,
      })
    })

    return chartData
  }, [data, data2, model, model2])

  // Stats from forecast
  const forecastStats = data?.forecast || []

  return (
    <div>
      <SectionHeader title="📈 AQI Forecast"
        sub="Historical trend + multi-model forward prediction" />

      {/* Controls row */}
      <div style={{
        display: 'flex', flexWrap: 'wrap', gap: '16px',
        marginBottom: '20px', alignItems: 'flex-end'
      }}>
        <CitySelect value={city} onChange={setCity} />

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label style={{
            fontSize: '11px', fontWeight: 600, color: '#7E909A',
            textTransform: 'uppercase', letterSpacing: '0.07em'
          }}>Model 1</label>
          <select value={model} onChange={e => setModel(e.target.value)}
            style={{
              background: '#fff', border: '1.5px solid #e5e7eb', color: '#1a2332',
              borderRadius: '10px', padding: '10px 14px', fontSize: '14px', outline: 'none',
              cursor: 'pointer', boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
            }}>
            {MODEL_OPTIONS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label style={{
            fontSize: '11px', fontWeight: 600, color: '#7E909A',
            textTransform: 'uppercase', letterSpacing: '0.07em'
          }}>Model 2</label>
          <select value={model2} onChange={e => setModel2(e.target.value)}
            style={{
              background: '#fff', border: '1.5px solid #e5e7eb', color: '#1a2332',
              borderRadius: '10px', padding: '10px 14px', fontSize: '14px', outline: 'none',
              cursor: 'pointer', boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
            }}>
            {MODEL_OPTIONS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label style={{
            fontSize: '11px', fontWeight: 600, color: '#7E909A',
            textTransform: 'uppercase', letterSpacing: '0.07em'
          }}>Forecast days: {days}</label>
          <input type="range" min={1} max={14} value={days}
            onChange={e => setDays(Number(e.target.value))}
            style={{ width: '120px', accentColor: '#1C4E80', marginTop: '6px' }} />
        </div>
      </div>



      {loading && <Spinner />}
      {error && <div style={{ marginBottom: '16px' }}><ErrorBox msg={error} /></div>}

      {!loading && filteredChartData.length > 0 && (
        <>
          <Card style={{ padding: '24px', marginBottom: '16px' }}>
            {/* AQI band legend */}
            <div style={{
              display: 'flex', gap: '16px', marginBottom: '16px',
              flexWrap: 'wrap', fontSize: '12px'
            }}>
              {[['Good', '#16a34a'], ['Satisfactory', '#65a30d'], ['Moderate', '#d97706'],
              ['Poor', '#ea580c'], ['Very Poor', '#dc2626'], ['Severe', '#7c3aed']].map(([l, c]) => (
                <span key={l} style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#4b5563' }}>
                  <span style={{
                    width: '10px', height: '10px', borderRadius: '50%',
                    background: c, display: 'inline-block'
                  }} />
                  {l}
                </span>
              ))}
            </div>

            <ResponsiveContainer width="100%" height={380}>
              <LineChart data={filteredChartData}
                margin={{ top: 10, right: 30, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis
                  dataKey="date"
                  stroke="#9ca3af"
                  tick={{ fontSize: 11 }}
                  minTickGap={45}
                />
                <YAxis stroke="#9ca3af" tick={{ fontSize: 11 }} domain={[0, 'auto']} />
                <Tooltip
                  contentStyle={{
                    background: '#fff', border: '1px solid #e5e7eb',
                    borderRadius: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                  }}
                  labelStyle={{ color: '#374151', fontWeight: 600 }}
                  itemStyle={{ color: '#374151' }} />
                <Legend wrapperStyle={{ paddingTop: '12px', fontSize: '13px' }} />

                {/* AQI threshold lines */}
                <ReferenceLine y={50} stroke="#16a34a" strokeDasharray="4 4"
                  label={{ value: 'Good', fill: '#16a34a', fontSize: 10, position: 'right' }} />
                <ReferenceLine y={100} stroke="#65a30d" strokeDasharray="4 4"
                  label={{ value: 'Sat.', fill: '#65a30d', fontSize: 10, position: 'right' }} />
                <ReferenceLine y={200} stroke="#d97706" strokeDasharray="4 4"
                  label={{ value: 'Mod.', fill: '#d97706', fontSize: 10, position: 'right' }} />
                <ReferenceLine y={300} stroke="#ea580c" strokeDasharray="4 4"
                  label={{ value: 'Poor', fill: '#ea580c', fontSize: 10, position: 'right' }} />

                <Line dataKey="Historical" stroke="#0091D5" strokeWidth={2}
                  dot={false} name="Historical" connectNulls={false}
                  activeDot={{ r: 4, fill: '#0091D5' }} />
                <Line dataKey={model} stroke="#7c3aed" strokeWidth={2}
                  strokeDasharray="6 3" dot={false}
                  name={`Forecast (${model})`} connectNulls={false} />
                {model !== model2 && (
                  <Line dataKey={model2} stroke="#ec4899" strokeWidth={2}
                    strokeDasharray="4 2" dot={false}
                    name={`Forecast (${model2})`} connectNulls={false} />
                )}

                {/* Brush = drag-to-zoom */}
                <Brush
                  dataKey="date"
                  height={32}
                  stroke="#1C4E80"
                  fill="#dbeafe"

                  startIndex={brushRange.startIndex}
                  endIndex={brushRange.endIndex}

                  travellerWidth={0}

                  tickFormatter={() => ""}

                  onChange={(e) => {

                    if (!e) return

                    const windowSize = 60

                    let start = e.startIndex
                    let end = start + windowSize


                    if (end >= filteredChartData.length) {
                      end = filteredChartData.length - 1
                      start = Math.max(0, end - windowSize)
                    }


                    setBrushRange({
                      startIndex: start,
                      endIndex: end
                    })

                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          {/* Forecast summary cards */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit,minmax(140px,1fr))', gap: '12px'
          }}>
            {forecastStats.map((f, i) => {
              const lvl = getAQILevel(f.predicted_aqi)
              return (
                <Card key={i} style={{
                  padding: '16px 20px',
                  borderTop: `3px solid ${lvl.hex}`
                }}>
                  <p style={{
                    fontSize: '11px', fontWeight: 600, color: '#7E909A',
                    textTransform: 'uppercase', letterSpacing: '0.07em',
                    marginBottom: '6px'
                  }}>Day +{f.day}</p>
                  <p style={{
                    fontSize: '28px', fontWeight: 900,
                    color: lvl.hex, lineHeight: 1
                  }}>{f.predicted_aqi}</p>
                  <p style={{
                    fontSize: '12px', color: '#6b7280',
                    marginTop: '6px'
                  }}>{f.category}</p>
                </Card>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}