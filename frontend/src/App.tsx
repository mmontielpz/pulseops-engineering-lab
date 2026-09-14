import { useState } from 'react'
import './App.css'
import { IncidentDetail } from './pages/IncidentDetail'
import { IncidentList } from './pages/IncidentList'
import { NewIncident } from './pages/NewIncident'

type View = { name: 'list' } | { name: 'detail'; id: string }

function App() {
  const [view, setView] = useState<View>({ name: 'list' })
  const [refreshKey, setRefreshKey] = useState(0)

  return (
    <div className="app">
      <header>
        <h1>PulseOps</h1>
        <p className="tagline">Incident &amp; support operations</p>
      </header>

      {view.name === 'list' && (
        <main>
          <NewIncident onCreated={() => setRefreshKey((k) => k + 1)} />
          <IncidentList refreshKey={refreshKey} onSelect={(id) => setView({ name: 'detail', id })} />
        </main>
      )}

      {view.name === 'detail' && (
        <main>
          <IncidentDetail incidentId={view.id} onBack={() => setView({ name: 'list' })} />
        </main>
      )}
    </div>
  )
}

export default App
