export const AQI_LEVELS = [
  { max: 50,   label: 'Good',         hex: '#16a34a', bg: '#f0fdf4', text: '#16a34a', border: '#bbf7d0' },
  { max: 100,  label: 'Satisfactory',  hex: '#65a30d', bg: '#f7fee7', text: '#65a30d', border: '#d9f99d' },
  { max: 200,  label: 'Moderate',     hex: '#d97706', bg: '#fffbeb', text: '#d97706', border: '#fde68a' },
  { max: 300,  label: 'Poor',         hex: '#ea580c', bg: '#fff7ed', text: '#ea580c', border: '#fed7aa' },
  { max: 400,  label: 'Very Poor',     hex: '#dc2626', bg: '#fef2f2', text: '#dc2626', border: '#fecaca' },
  { max: 9999, label: 'Severe',       hex: '#7c3aed', bg: '#f5f3ff', text: '#7c3aed', border: '#ddd6fe' },
]

export function getAQILevel(aqi) {
  return AQI_LEVELS.find(l => aqi <= l.max) || AQI_LEVELS[5]
}

export function AQICard({ city, aqi, category, subtitle }) {
  const level = getAQILevel(aqi)
  return (
    <div style={{
      background: '#ffffff',
      borderRadius: '20px',
      overflow: 'hidden',
      boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.06)',
      transition: 'transform 0.2s, box-shadow 0.2s',
      cursor: 'default',
    }}
    onMouseEnter={e => {
      e.currentTarget.style.transform = 'translateY(-2px)'
      e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.07), 0 12px 32px rgba(0,0,0,0.1)'
    }}
    onMouseLeave={e => {
      e.currentTarget.style.transform = 'translateY(0)'
      e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.06)'
    }}>
      {/* Colored top strip */}
      <div style={{height: '5px', background: level.hex}}/>
      <div style={{padding: '20px 24px 24px'}}>
        <div style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:'12px'}}>
          <div>
            <p style={{fontSize:'11px', fontWeight:600, letterSpacing:'0.08em',
              color:'#9ca3af', textTransform:'uppercase', marginBottom:'4px'}}>
              {subtitle || 'Current AQI'}
            </p>
            <p style={{fontSize:'17px', fontWeight:700, color:'#111827'}}>{city}</p>
          </div>
          <span style={{fontSize:'28px'}}>{level.emoji}</span>
        </div>
        <p style={{fontSize:'60px', fontWeight:900, lineHeight:1,
          color: level.hex, margin:'8px 0 14px'}}>
          {aqi}
        </p>
        <span style={{
          display:'inline-flex', alignItems:'center', gap:'6px',
          padding:'5px 14px', borderRadius:'999px',
          background: level.bg, color: level.text,
          fontSize:'12px', fontWeight:700,
          border: `1px solid ${level.border}`,
        }}>
          {category || level.label}
        </span>
      </div>
    </div>
  )
}

export function CitySelect({ value, onChange, label = 'City' }) {
  const cities = ['Delhi','Mumbai','Bangalore','Hyderabad','Chennai']
  const flags  = { Delhi:'', Mumbai:'', Bangalore:'', Hyderabad:'', Chennai:'' }
  return (
    <div style={{display:'flex', flexDirection:'column', gap:'6px'}}>
      {label && <label style={{fontSize:'12px', fontWeight:600, color:'#6b7280',
        textTransform:'uppercase', letterSpacing:'0.06em'}}>{label}</label>}
      <select value={value} onChange={e => onChange(e.target.value)} style={{
        background:'#fff', border:'1.5px solid #e5e7eb', color:'#111827',
        borderRadius:'10px', padding:'10px 16px', fontSize:'14px', fontWeight:500,
        outline:'none', cursor:'pointer', minWidth:'180px',
        boxShadow:'0 1px 2px rgba(0,0,0,0.04)',
      }}>
        {cities.map(c => (
          <option key={c} value={c}>{flags[c]} {c}</option>
        ))}
      </select>
    </div>
  )
}

export function Spinner() {
  return (
    <div style={{display:'flex', flexDirection:'column', justifyContent:'center',
      alignItems:'center', height:'160px', gap:'12px'}}>
      <div style={{width:'36px', height:'36px', border:'3px solid #e5e7eb',
        borderTopColor:'#3b82f6', borderRadius:'50%', animation:'spin 0.7s linear infinite'}}/>
      <span style={{fontSize:'13px', color:'#9ca3af'}}>Loading data...</span>
      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
    </div>
  )
}

export function ErrorBox({ msg }) {
  return (
    <div style={{background:'#fef2f2', border:'1px solid #fecaca', color:'#b91c1c',
      borderRadius:'12px', padding:'16px 20px', fontSize:'14px', display:'flex',
      alignItems:'center', gap:'10px'}}>
      <span style={{fontSize:'20px'}}>⚠️</span> {msg}
    </div>
  )
}

export function SectionHeader({ title, sub }) {
  return (
    <div style={{marginBottom:'28px'}}>
      <h1 style={{fontSize:'28px', fontWeight:800, color:'#111827', letterSpacing:'-0.5px'}}>{title}</h1>
      {sub && <p style={{fontSize:'14px', color:'#6b7280', marginTop:'5px'}}>{sub}</p>}
    </div>
  )
}

export function StatCard({ label, value, sub, color }) {
  return (
    <div style={{background:'#fff', borderRadius:'14px', padding:'18px 20px',
      boxShadow:'0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04)'}}>
      <p style={{fontSize:'11px', fontWeight:600, color:'#9ca3af',
        textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:'8px'}}>{label}</p>
      <p style={{fontSize:'24px', fontWeight:800, color: color || '#111827'}}>{value}</p>
      {sub && <p style={{fontSize:'12px', color:'#9ca3af', marginTop:'4px'}}>{sub}</p>}
    </div>
  )
}