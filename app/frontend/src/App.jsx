import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Home      from './pages/Home'
import Forecast  from './pages/Forecast'
import Compare   from './pages/Compare'
import Explain   from './pages/Explain'
import Advisory  from './pages/Advisory'

const NAV = [
  { to: '/',         label: 'Command Center', icon: '⚡' },
  { to: '/forecast', label: 'Forecast',       icon: '📈' },
  { to: '/compare',  label: 'Compare',        icon: '🏙️' },
  { to: '/explain',  label: 'Explain',        icon: '🔍' },
  { to: '/advisory', label: 'Advisory',       icon: '🩺' },
]

export default function App() {
  return (
    <BrowserRouter>
      <div style={{minHeight:'100vh', background:'#f4f6f9', fontFamily:'Inter, -apple-system, sans-serif'}}>

        <nav style={{
          background:'#1C4E80',
          padding:'0 40px',
          display:'flex', alignItems:'center', gap:'4px',
          position:'sticky', top:0, zIndex:50,
          height:'56px',
          boxShadow:'0 2px 8px rgba(28,78,128,0.3)',
        }}>
          {/* Logo */}
          <div style={{display:'flex', alignItems:'center', gap:'10px', marginRight:'32px'}}>
            <div style={{width:'30px', height:'30px', background:'rgba(255,255,255,0.15)',
              borderRadius:'8px', display:'flex', alignItems:'center',
              justifyContent:'center', fontSize:'15px'}}>🌫️</div>
            <div>
              <span style={{fontWeight:800, fontSize:'14px', color:'#ffffff'}}>AirIntel</span>
              <span style={{fontWeight:800, fontSize:'14px', color:'#A5D8DD'}}> AI</span>
              <div style={{fontSize:'9px', color:'rgba(255,255,255,0.45)', marginTop:'1px'}}>
                Urban Air Quality Intelligence
              </div>
            </div>
          </div>

          {NAV.map(({to, label, icon}) => (
            <NavLink key={to} to={to} end={to==='/'}
              style={({isActive}) => ({
                display:'flex', alignItems:'center', gap:'5px',
                padding:'5px 13px', borderRadius:'6px',
                fontSize:'13px', fontWeight: isActive ? 600 : 400,
                textDecoration:'none', transition:'all 0.15s',
                background: isActive ? 'rgba(255,255,255,0.15)' : 'transparent',
                color: isActive ? '#ffffff' : 'rgba(255,255,255,0.6)',
                border: 'none',
              })}>
              <span style={{fontSize:'13px'}}>{icon}</span>
              {label}
            </NavLink>
          ))}

          <div >
            
          </div>
        </nav>

        <main style={{maxWidth:'1200px', margin:'0 auto', padding:'32px 28px'}}>
          <Routes>
            <Route path="/"          element={<Home />}     />
            <Route path="/forecast"  element={<Forecast />} />
            <Route path="/compare"   element={<Compare />}  />
            <Route path="/explain"   element={<Explain />}  />
            <Route path="/advisory"  element={<Advisory />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}