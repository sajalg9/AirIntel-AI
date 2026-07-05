import { useState, useEffect } from 'react'
import axios from 'axios'
import { CitySelect, Spinner, ErrorBox, SectionHeader, getAQILevel } from '../components/AQIUtils'

const API = '/api'

// Indic language advisory templates (IndicTrans2/MuRIL used for production translation)
const INDIC_ADVISORY = {
  Delhi: {
    lang: 'Hindi',
    Good:      'वायु गुणवत्ता अच्छी है। बाहर सामान्य गतिविधि ठीक है।',
    Moderate:  'संवेदनशील व्यक्तियों को लंबे समय तक बाहर रहने से बचना चाहिए।',
    Poor:      'बाहरी गतिविधि सीमित करें। मास्क पहनें।',
    'Very Poor':'बाहर न जाएं। संवेदनशील समूहों के लिए स्वास्थ्य अलर्ट।',
    Severe:    'आपातकालीन स्वास्थ्य चेतावनी। घर के अंदर रहें।',
  },
  Mumbai: {
    lang: 'Marathi',
    Good:      'हवेची गुणवत्ता चांगली आहे. सामान्य बाहेरचे उपक्रम ठीक आहेत.',
    Moderate:  'संवेदनशील व्यक्तींनी दीर्घकाळ बाहेर राहणे टाळावे.',
    Poor:      'बाहेरचे उपक्रम मर्यादित करा. मास्क घाला.',
    'Very Poor':'बाहेर जाऊ नका. आरोग्य सूचना.',
    Severe:    'आपत्कालीन आरोग्य इशारा. घरातच राहा.',
  },
  Bangalore: {
    lang: 'Kannada',
    Good:      'ಗಾಳಿಯ ಗುಣಮಟ್ಟ ಒಳ್ಳೆಯದಾಗಿದೆ. ಸಾಮಾನ್ಯ ಚಟುವಟಿಕೆ ಸರಿ.',
    Moderate:  'ಸೂಕ್ಷ್ಮ ವ್ಯಕ್ತಿಗಳು ಹೊರಗೆ ಹೆಚ್ಚು ಸಮಯ ಕಳೆಯುವುದನ್ನು ತಪ್ಪಿಸಿ.',
    Poor:      'ಹೊರಗಿನ ಚಟುವಟಿಕೆ ಮಿತಿಗೊಳಿಸಿ. ಮಾಸ್ಕ್ ಧರಿಸಿ.',
    'Very Poor':'ಹೊರಗೆ ಹೋಗಬೇಡಿ. ಆರೋಗ್ಯ ಎಚ್ಚರಿಕೆ.',
    Severe:    'ತುರ್ತು ಆರೋಗ್ಯ ಎಚ್ಚರಿಕೆ. ಒಳಗೆ ಇರಿ.',
  },
  Chennai: {
    lang: 'Tamil',
    Good:      'காற்றின் தரம் நல்லது. வெளியில் சாதாரண செயல்பாடு சரி.',
    Moderate:  'உணர்திறன் உள்ளவர்கள் நீண்ட நேரம் வெளியில் இருப்பதை தவிர்க்கவும்.',
    Poor:      'வெளி செயல்பாட்டை கட்டுப்படுத்துங்கள். முகமூடி அணியுங்கள்.',
    'Very Poor':'வெளியில் செல்லாதீர்கள். சுகாதார எச்சரிக்கை.',
    Severe:    'அவசர சுகாதார எச்சரிக்கை. உள்ளே இருங்கள்.',
  },
  Hyderabad: {
    lang: 'Telugu',
    Good:      'గాలి నాణ్యత మంచిది. సాధారణ బయటి కార్యకలాపాలు సరే.',
    Moderate:  'సున్నితమైన వ్యక్తులు ఎక్కువ సేపు బయట ఉండటం మానుకోండి.',
    Poor:      'బయటి కార్యకలాపాలు పరిమితం చేయండి. మాస్క్ ధరించండి.',
    'Very Poor':'బయటకు వెళ్ళకండి. ఆరోగ్య హెచ్చరిక.',
    Severe:    'అత్యవసర ఆరోగ్య హెచ్చరిక. లోపల ఉండండి.',
  },
}

const RISK_COLORS = {
  Low:      { bg: 'bg-green-50',  border: 'border-green-200',  text: 'text-green-700'  },
  Moderate: { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-700' },
  High:     { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700' },
  'Very High':{ bg:'bg-red-50',   border: 'border-red-200',    text: 'text-red-700'    },
  Critical: { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-700' },
}

export default function Advisory() {
  const [city,    setCity]    = useState('Delhi')
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  async function fetchAdvisory(c) {
    setLoading(true); setError(null)
    try {
      const res = await axios.post(`${API}/advisory`, { city: c, model: 'random_forest' })
      setData(res.data)
    } catch(e) { setError(e.message) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchAdvisory(city) }, [city])

  const risk    = data ? RISK_COLORS[data.risk_level] || RISK_COLORS['Moderate'] : null
  const aqi_lvl = data ? getAQILevel(data.predicted_aqi) : null
  const indic   = data ? INDIC_ADVISORY[city] : null
  const indic_text = indic
    ? (indic[data.category] || indic['Moderate'])
    : null

  return (
    <div>
      <SectionHeader title="🩺 Health Advisory"
        sub="AI-generated intervention recommendations + multilingual citizen alerts" />

      <div className="mb-6 rounded-3xl border border-slate-100 bg-white p-4 shadow-md">
        <CitySelect value={city} onChange={c => { setCity(c); }} />
      </div>

      {loading && <Spinner />}
      {error   && <ErrorBox msg={error} />}

      {!loading && data && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

          {/* AQI + risk level */}
          <div className={`${risk.bg} border ${risk.border} rounded-3xl p-6 flex flex-col gap-3 shadow-md`}>
            <p className="text-sm uppercase tracking-wider text-slate-500">Predicted AQI</p>
            <p className={`text-5xl font-black ${aqi_lvl.text}`}>{data.predicted_aqi}</p>
            <span className={`self-start rounded-full px-3 py-1 text-sm font-semibold text-white ${aqi_lvl.bg}`}>
              {data.category}
            </span>
            <div className={`mt-2 border-t ${risk.border} pt-3`}>
              <p className="mb-1 text-xs text-slate-400">Risk Level</p>
              <p className={`text-xl font-bold ${risk.text}`}>{data.risk_level}</p>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-slate-700">{data.health_advisory}</p>
          </div>

          {/* Interventions */}
          <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-md">
            <h3 className="mb-4 text-sm uppercase tracking-wider text-slate-500">
              Government Interventions
            </h3>
            <ul className="flex flex-col gap-3">
              {data.interventions.map((item, i) => (
                <li key={i} className="flex gap-3 text-sm leading-relaxed text-slate-700">
                  <span className="mt-0.5 shrink-0 font-bold text-sky-500">{i+1}.</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>

          {/* Indic advisory */}
          <div className="flex flex-col gap-4 rounded-3xl border border-indigo-100 bg-indigo-50 p-6 shadow-md">
            <div className="flex items-center justify-between">
              <h3 className="text-sm uppercase tracking-wider text-indigo-900">Citizen Advisory</h3>
              {indic && (
                <span className="rounded-full bg-indigo-100 px-2 py-0.5 text-xs text-indigo-700">
                  {indic.lang}
                </span>
              )}
            </div>

            {indic_text && (
              <p className="text-lg font-medium leading-relaxed text-indigo-950">{indic_text}</p>
            )}
            <p className="text-sm leading-relaxed text-indigo-900">{data.health_advisory}</p>

            <div className="mt-auto border-t border-indigo-100 pt-3 text-xs text-indigo-700">
              Multilingual output powered by IndicTrans2 / MuRIL.<br/>
              Languages: Hindi · Marathi · Kannada · Tamil · Telugu
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
