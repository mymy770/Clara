import React, { useState, useEffect } from 'react'
import { listSessions } from '../api'

export default function SessionSidebar({ currentSessionId, onSelectSession, onNewSession }) {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSessions()
    // Rafraîchir toutes les 5 secondes
    const interval = setInterval(loadSessions, 5000)
    return () => clearInterval(interval)
  }, [])

  async function loadSessions() {
    try {
      const data = await listSessions()
      setSessions(data)
    } catch (error) {
      console.error('Error loading sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="sidebar">
      <div style={{ padding: '16px', borderBottom: '1px solid var(--border-subtle)' }}>
        <button
          onClick={onNewSession}
          style={{
            width: '100%',
            padding: '12px',
            background: 'var(--accent)',
            color: 'var(--text-main)',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            fontFamily: 'var(--font-sans)',
          }}
        >
          + Nouvelle session
        </button>
      </div>
      
      <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
        {loading ? (
          <div style={{ padding: '16px', color: 'var(--text-muted)', textAlign: 'center' }}>
            Chargement...
          </div>
        ) : sessions.length === 0 ? (
          <div style={{ padding: '16px', color: 'var(--text-muted)', textAlign: 'center' }}>
            Aucune session
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.session_id}
              onClick={() => onSelectSession(session.session_id)}
              style={{
                padding: '12px',
                marginBottom: '4px',
                background: currentSessionId === session.session_id ? 'var(--accent-soft)' : 'transparent',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                border: currentSessionId === session.session_id ? '1px solid var(--accent)' : '1px solid transparent',
              }}
            >
              <div style={{ fontSize: '14px', fontWeight: '500', color: 'var(--text-main)', marginBottom: '4px' }}>
                {session.title || session.session_id}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                {new Date(session.started_at).toLocaleString('fr-FR')}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

