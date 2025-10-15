import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import { getHealth, getModelInfo, getStatistics, formatThroughputFromStats } from './api'

function App() {
  const [apiStatus, setApiStatus] = React.useState<'loading' | 'up' | 'down'>('loading')
  const [modelName, setModelName] = React.useState<string>('Loading...')
  const [throughput, setThroughput] = React.useState<string>('-- req/s')

  React.useEffect(() => {
    let isMounted = true
    async function load() {
      try {
        const health = await getHealth()
        if (!isMounted) return
        setApiStatus(health?.status === 'ok' ? 'up' : 'down')
      } catch {
        if (!isMounted) return
        setApiStatus('down')
      }
      try {
        const info = await getModelInfo()
        if (!isMounted) return
        const name = info?.model_name || info?.xgb_version || 'Hybrid Model'
        setModelName(String(name))
        if (typeof info?.requests_per_min === 'number') {
          const perSec = info.requests_per_min / 60
          setThroughput(`${perSec.toFixed(2)} req/s`)
        } else {
          // fallback to statistics
          try {
            const stats = await getStatistics()
            if (!isMounted) return
            setThroughput(formatThroughputFromStats(stats))
          } catch {
            /* ignore */
          }
        }
      } catch {
        if (!isMounted) return
        setModelName('Unavailable')
        try {
          const stats = await getStatistics()
          if (!isMounted) return
          setThroughput(formatThroughputFromStats(stats))
        } catch {
          /* ignore */
        }
      }
    }
    load()
    const id = setInterval(load, 5000)
    return () => {
      isMounted = false
      clearInterval(id)
    }
  }, [])

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <header className="border-b border-slate-800/60 bg-slate-900/40 backdrop-blur">
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold">Insider Intelligence Dashboard</h1>
          <nav className="flex gap-4 text-sm text-slate-300">
            <a href="#" className="hover:text-white">Overview</a>
            <a href="#" className="hover:text-white">Analysis</a>
            <a href="#" className="hover:text-white">Intelligence</a>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6 py-8">
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="rounded-xl bg-[var(--panel)] border border-slate-800/60 p-5">
            <p className="text-slate-400 text-sm">API Status</p>
            <p className={`mt-3 text-2xl font-semibold ${apiStatus === 'up' ? 'text-emerald-400' : apiStatus === 'down' ? 'text-rose-400' : ''}`}>
              {apiStatus === 'loading' ? 'Checking...' : apiStatus === 'up' ? 'Online' : 'Offline'}
            </p>
          </div>
          <div className="rounded-xl bg-[var(--panel)] border border-slate-800/60 p-5">
            <p className="text-slate-400 text-sm">Model</p>
            <p className="mt-3 text-2xl font-semibold truncate" title={modelName}>{modelName}</p>
          </div>
          <div className="rounded-xl bg-[var(--panel)] border border-slate-800/60 p-5">
            <p className="text-slate-400 text-sm">Throughput</p>
            <p className="mt-3 text-2xl font-semibold">{throughput}</p>
          </div>
        </section>
      </main>
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
