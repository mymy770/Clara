import React, { useState, useEffect } from 'react'
import { listSessions, renameSession, deleteSession, deleteAllSessions } from '../api'

export default function SessionSidebar({ currentSessionId, onSelectSession, onNewSession }) {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState(null)

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

  async function handleRename(session) {
    const newTitle = prompt('Nouveau nom pour la session:', session.title || session.session_id)
    if (newTitle && newTitle.trim()) {
      try {
        await renameSession(session.session_id, newTitle.trim())
        loadSessions()
      } catch (error) {
        console.error('Error renaming session:', error)
        alert(`Erreur: ${error.message}`)
      }
    }
  }

  async function handleDelete(sessionId) {
    if (window.confirm('Supprimer cette session ? Cette action est définitive.')) {
      try {
        await deleteSession(sessionId)
        loadSessions()
        if (currentSessionId === sessionId) {
          onNewSession()
        }
      } catch (error) {
        console.error('Error deleting session:', error)
        alert(`Erreur: ${error.message}`)
      }
    }
  }

  async function handleDeleteAll() {
    if (window.confirm('Supprimer toutes les sessions ? Cette action est définitive.')) {
      try {
        await deleteAllSessions()
        loadSessions()
        onNewSession()
      } catch (error) {
        console.error('Error deleting all sessions:', error)
        alert(`Erreur: ${error.message}`)
      }
    }
  }

  return (
    <div className="sidebar">
      <div style={{ padding: '16px', borderBottom: '1px solid var(--borderSubtle)' }}>
        <button
          onClick={onNewSession}
          style={{
            width: '100%',
            padding: '12px',
            background: 'var(--accent)',
            color: 'var(--textPrimary)',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            fontFamily: 'var(--font-sans)',
            marginBottom: '8px',
          }}
        >
          + Nouvelle session
        </button>
        <button
          onClick={handleDeleteAll}
          style={{
            width: '100%',
            padding: '8px',
            background: 'transparent',
            color: 'var(--textSecondary)',
            border: '1px solid var(--borderSubtle)',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            fontSize: '12px',
            fontFamily: 'var(--font-sans)',
          }}
        >
          Supprimer toutes les sessions
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
              style={{
                padding: '8px',
                marginBottom: '4px',
                background: currentSessionId === session.session_id ? 'var(--accent)' : 'transparent',
                borderRadius: 'var(--radius-sm)',
                border: currentSessionId === session.session_id ? '1px solid var(--accent)' : '1px solid transparent',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '8px',
              }}
            >
              <div
                onClick={() => onSelectSession(session.session_id)}
                style={{
                  flex: 1,
                  cursor: 'pointer',
                }}
              >
                <div style={{ fontSize: '14px', fontWeight: '500', color: 'var(--textPrimary)', marginBottom: '4px' }}>
                  {session.title || session.session_id}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--textSecondary)' }}>
                  {new Date(session.started_at).toLocaleString('fr-FR')}
                </div>
              </div>
              <div style={{ display: 'flex', gap: '4px' }}>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleRename(session)
                  }}
                  style={{
                    padding: '4px 8px',
                    background: 'transparent',
                    color: 'var(--textSecondary)',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '14px',
                  }}
                  title="Renommer"
                >
                  ✏️
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDelete(session.session_id)
                  }}
                  style={{
                    padding: '4px 8px',
                    background: 'transparent',
                    color: 'var(--textSecondary)',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '14px',
                  }}
                  title="Supprimer"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

