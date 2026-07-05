import { useEffect, useState } from 'react'
import axios from 'axios'
import { AQICard, CitySelect, Spinner, ErrorBox, getAQILevel } from '../components/AQIUtils'

const API = '/api'

const POLLUTANT_META = {
  'PM2.5': { color: '#0091D5', icon: '💨', desc: 'Fine particles'  },
  'PM10':  { color: '#6366f1', icon: '🌫️', desc: 'Coarse dust'    },
  'NO2':   { color: '#f59e0b', icon: '🚗', desc: 'Vehicle exhaust' },
  'SO2':   { color: '#ef4444', icon: '🏭', desc: 'Industrial'      },
  'CO':    { color: '#6b7280', icon: '♨️',  desc: 'Combustion'     },
  'O3':    { color: '#10b981', icon: '☀️', desc: 'Photochemical'   },
}

function Card({ children, style }) {
  return (
    <div style={{
      background:'#ffffff', borderRadius:'14px',
      boxShadow:'0 1px 3px rgba(0,0,0,0.07), 0 4px 16px rgba(0,0,0,0.05)',
      ...style
    }}>
      {children}
    </div>
  )
}

export default function Home() {
  const [city, setCity]       = useState('Delhi')
  const [current, setCurrent] = useState(null)
  const [forecast, setFcast]  = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  async function fetchAll(c) {
    setLoading(true); setError(null)
    try {
      const [cur, fcast] = await Promise.all([
        axios.get(`${API}/current/${c}`),
        axios.post(`${API}/forecast`, { city: c, days_ahead: 3, model: 'random_forest' })
      ])
      setCurrent(cur.data); setFcast(fcast.data)
    } catch(e) { setError(e.message) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchAll(city) }, [city])

  const level = current ? getAQILevel(current.AQI) : null

  return (
    <div>
      {/* Page header */}
      <div style={{display:'flex', justifyContent:'space-between',
        alignItems:'flex-start', marginBottom:'24px', flexWrap:'wrap', gap:'16px'}}>
        <div>
          <h1 style={{fontSize:'26px', fontWeight:800, color:'#1a2332', letterSpacing:'-0.3px'}}>
            ⚡ Command Center
          </h1>
          <p style={{fontSize:'14px', color:'#7E909A', marginTop:'4px'}}>
            Real-time air quality intelligence · 5 Indian cities
          </p>
        </div>
        <CitySelect value={city} onChange={c => setCity(c)} />
      </div>

      {loading && <Spinner />}
      {error   && <div style={{marginBottom:'16px'}}><ErrorBox msg={error}/></div>}

      {!loading && current && (
        <>
          {/* AQI forecast cards */}
          <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(210px,1fr))',
            gap:'14px', marginBottom:'18px'}}>
            <AQICard city={city} aqi={current.AQI}
              category={current.category} subtitle="Current AQI"/>
            {forecast?.forecast?.map((f,i) => (
              <AQICard key={i} city={`Day +${f.day}`}
                aqi={f.predicted_aqi} category={f.category}
                subtitle={`${24*(i+1)}hr Forecast`}/>
            ))}
          </div>

          {/* Summary strip */}
          <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(150px,1fr))',
            gap:'12px', marginBottom:'18px'}}>
            {[
              { label:'Status',     value: current.category, color: level.hex },
              { label:'Top Pollutant',
                value: Object.entries(current.pollutant_pct||{}).sort((a,b)=>b[1]-a[1])[0]?.[0]||'—' },
              { label:'24hr Trend',
                value: forecast?.forecast?.[0]?.predicted_aqi > current.AQI ? '↑ Rising':'↓ Falling',
                color: forecast?.forecast?.[0]?.predicted_aqi > current.AQI ? '#ef4444':'#16a34a' },
              { label:'Last Updated', value: current.date },
            ].map(({label,value,color}) => (
              <Card key={label} style={{padding:'16px 20px'}}>
                <p style={{fontSize:'11px', fontWeight:600, color:'#7E909A',
                  textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:'6px'}}>{label}</p>
                <p style={{fontSize:'20px', fontWeight:800, color: color||'#1a2332'}}>{value}</p>
              </Card>
            ))}
          </div>

          {/* Pollutant breakdown */}
          <Card style={{padding:'24px'}}>
            <div style={{display:'flex', justifyContent:'space-between',
              alignItems:'center', marginBottom:'18px'}}>
              <h2 style={{fontSize:'16px', fontWeight:700, color:'#1a2332'}}>
                🧪 Pollutant Breakdown
              </h2>
              <span >
                
              </span>
            </div>

            <div style={{display:'grid',
              gridTemplateColumns:'repeat(auto-fit,minmax(155px,1fr))', gap:'12px'}}>
              {Object.entries(POLLUTANT_META).map(([pol, meta]) => {
                const val = current[pol]
                const pct = current.pollutant_pct?.[pol] || 0
                return (
                  <div key={pol} style={{background:'#f8fafc', borderRadius:'12px',
                    padding:'14px 16px', borderLeft:`3px solid ${meta.color}`}}>
                    <div style={{display:'flex', justifyContent:'space-between', marginBottom:'6px'}}>
                      <span style={{fontSize:'18px'}}>{meta.icon}</span>
                      <span style={{fontSize:'10px', color:'#7E909A',
                        background:'#fff', padding:'2px 6px', borderRadius:'4px'}}>{meta.desc}</span>
                    </div>
                    <p style={{fontSize:'11px', fontWeight:700, color:'#7E909A',
                      textTransform:'uppercase', letterSpacing:'0.06em'}}>{pol}</p>
                    <p style={{fontSize:'20px', fontWeight:800, color:'#1a2332', margin:'2px 0'}}>{val}</p>
                    <p style={{fontSize:'10px', color:'#7E909A', marginBottom:'8px'}}>μg/m³</p>
                    <div style={{height:'4px', background:'#e2e8f0', borderRadius:'99px'}}>
                      <div style={{height:'4px', borderRadius:'99px', background:meta.color,
                        width:`${Math.min(pct,100)}%`}}/>
                    </div>
                    <p style={{fontSize:'11px', fontWeight:700,
                      color:meta.color, marginTop:'4px'}}>{pct}%</p>
                  </div>
                )
              })}
            </div>
          </Card>
        </>
      )}
    </div>
  )
}