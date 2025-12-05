import React, { useState, useEffect } from 'react'
import { listSessions, renameSession, deleteSession, deleteAllSessions, createSession } from '../api'
import ConfirmModal from './ConfirmModal'
import AppearanceSettings from './AppearanceSettings'

export default function SessionSidebarV2({ currentSessionId, onSelectSession, onNewSession }) {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState(null)
  const [editingValue, setEditingValue] = useState('')
  const [showConfirm, setShowConfirm] = useState(false)
  const [confirmMessage, setConfirmMessage] = useState('')
  const [confirmCallback, setConfirmCallback] = useState(null)
  const [showSettings, setShowSettings] = useState(false)

  useEffect(() => {
    console.log('SessionSidebarV2 mounted')
    loadSessions()
    const interval = setInterval(loadSessions, 5000)
    return () => clearInterval(interval)
  }, [])

  // Auto-select first session if none selected
  useEffect(() => {
    if (!currentSessionId && sessions.length > 0) {
      onSelectSession(sessions[0].session_id)
    }
  }, [sessions, currentSessionId])

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

  async function handleCreateSession() {
    try {
      const data = await createSession()
      await loadSessions()
      if (data.session_id) {
        onSelectSession(data.session_id)
      }
    } catch (error) {
      console.error('Error creating session:', error)
      alert(`Erreur: ${error.message}`)
    }
  }

  function handleStartRename(session, e) {
    e.stopPropagation()
    setEditingId(session.session_id)
    setEditingValue(session.title || session.session_id.replace(/\.txt$/, ''))
  }

  async function handleFinishRename(session, commit) {
    if (!commit || !editingValue.trim() || editingValue === (session.title || session.session_id.replace(/\.txt$/, ''))) {
      setEditingId(null)
      setEditingValue('')
      return
    }

    try {
      await renameSession(session.session_id, editingValue.trim())
      await loadSessions()
      setEditingId(null)
      setEditingValue('')
    } catch (error) {
      console.error('Error renaming session:', error)
      alert(`Erreur: ${error.message}`)
      setEditingId(null)
      setEditingValue('')
    }
  }

  function handleDelete(sessionId, e) {
    e.stopPropagation()
    setConfirmMessage('Êtes-vous sûr de vouloir supprimer cette session ?')
    setConfirmCallback(() => async () => {
      const wasCurrentSession = (currentSessionId === sessionId)
      try {
        await deleteSession(sessionId)
        await loadSessions()
        if (wasCurrentSession) {
          onNewSession()
          // Si d'autres sessions existent, sélectionner la première
          const updatedSessions = await listSessions()
          if (updatedSessions.length > 0) {
            onSelectSession(updatedSessions[0].session_id)
          }
        }
      } catch (error) {
        console.error('Error deleting session:', error)
        alert(`Erreur: ${error.message}`)
      }
    })
    setShowConfirm(true)
  }

  function handleDeleteAll() {
    if (sessions.length === 0) return
    setConfirmMessage(`Supprimer toutes les ${sessions.length} conversation(s) ?`)
    setConfirmCallback(() => async () => {
      try {
        for (const session of sessions) {
          await deleteSession(session.session_id)
        }
        await loadSessions()
        onNewSession()
      } catch (error) {
        console.error('Error deleting all sessions:', error)
        alert(`Erreur: ${error.message}`)
      }
    })
    setShowConfirm(true)
  }

  return (
    <>
      <div className="sidebar" style={{
        width: '260px',
        borderRight: '1px solid var(--sidebar-border)',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--sidebar-bg)',
        color: 'var(--sidebar-text)',
      }}>
        <div className="sidebar-header" style={{
          padding: '10px',
          borderBottom: '1px solid var(--sidebar-border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '13px',
          background: 'var(--sidebar-header-bg)',
          color: 'var(--sidebar-header-text)',
        }}>
          <span>Conversations</span>
          <button
            onClick={handleCreateSession}
            style={{
              padding: '4px 8px',
              fontSize: '12px',
              cursor: 'pointer',
              border: '1px solid var(--new-session-btn-border)',
              borderRadius: '4px',
              background: 'var(--new-session-btn-bg)',
              color: 'var(--new-session-btn-text)',
            }}
          >
            + Nouvelle
          </button>
        </div>

        <div className="session-list" style={{
          flex: 1,
          overflowY: 'auto',
        }}>
          {loading ? (
            <div style={{ padding: '16px', color: 'var(--sidebar-text)', textAlign: 'center', fontSize: '12px' }}>
              Chargement...
            </div>
          ) : sessions.length === 0 ? (
            <div style={{ padding: '16px', color: 'var(--sidebar-text)', textAlign: 'center', fontSize: '12px' }}>
              Aucune session
            </div>
          ) : (
            sessions.map((session) => {
              const isEditing = editingId === session.session_id
              const label = (session.title || session.session_id).replace(/\.txt$/, '')
              return (
                <div
                  key={session.session_id}
                  className={`session-item ${currentSessionId === session.session_id ? 'active' : ''}`}
                  onClick={() => !isEditing && onSelectSession(session.session_id)}
                  style={{
                    padding: '6px 8px',
                    borderBottom: '1px solid var(--sidebar-border)',
                    cursor: isEditing ? 'default' : 'pointer',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '6px',
                    color: 'var(--sidebar-text)',
                    background: currentSessionId === session.session_id ? 'rgba(0, 0, 0, 0.05)' : 'transparent',
                    fontWeight: currentSessionId === session.session_id ? '600' : '400',
                  }}
                >
                  {isEditing ? (
                    <input
                      type="text"
                      value={editingValue}
                      onChange={(e) => setEditingValue(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleFinishRename(session, true)
                        } else if (e.key === 'Escape') {
                          handleFinishRename(session, false)
                        }
                      }}
                      onBlur={() => handleFinishRename(session, true)}
                      autoFocus
                      style={{
                        flex: 1,
                        width: '100%',
                        padding: '2px 4px',
                        fontSize: '12px',
                        border: '1px solid var(--sidebar-border)',
                        borderRadius: '4px',
                        background: 'var(--sidebar-bg)',
                        color: 'var(--sidebar-text)',
                      }}
                    />
                  ) : (
                    <span className="session-title" style={{
                      flex: 1,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      color: 'var(--sidebar-text)',
                    }}>
                      {label || 'Sans titre'}
                    </span>
                  )}
                  {!isEditing && (
                    <div className="session-actions" style={{
                      display: 'flex',
                      gap: '4px',
                      flexShrink: 0,
                    }}>
                      <button
                        className="rename-btn"
                        onClick={(e) => handleStartRename(session, e)}
                        title="Renommer"
                        style={{
                          border: 'none',
                          background: 'transparent',
                          cursor: 'pointer',
                          fontSize: '13px',
                          padding: '4px 6px',
                          color: 'var(--sidebar-text)',
                          opacity: 0.5,
                          borderRadius: '4px',
                          transition: 'all 0.2s',
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.opacity = '1'
                          e.target.style.background = 'rgba(0, 0, 0, 0.05)'
                          e.target.style.color = '#007AFF'
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.opacity = '0.5'
                          e.target.style.background = 'transparent'
                          e.target.style.color = 'var(--sidebar-text)'
                        }}
                      >
                        ✏
                      </button>
                      <button
                        className="delete-btn"
                        onClick={(e) => handleDelete(session.session_id, e)}
                        title="Supprimer"
                        style={{
                          border: 'none',
                          background: 'transparent',
                          cursor: 'pointer',
                          fontSize: '13px',
                          padding: '4px 6px',
                          color: 'var(--sidebar-text)',
                          opacity: 0.5,
                          borderRadius: '4px',
                          transition: 'all 0.2s',
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.opacity = '1'
                          e.target.style.background = 'rgba(0, 0, 0, 0.05)'
                          e.target.style.color = '#ff3b30'
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.opacity = '0.5'
                          e.target.style.background = 'transparent'
                          e.target.style.color = 'var(--sidebar-text)'
                        }}
                      >
                        🗑
                      </button>
                    </div>
                  )}
                </div>
              )
            })
          )}
        </div>

        <div className="sidebar-footer" style={{
          padding: '12px 8px',
          borderTop: '1px solid var(--input-border)',
          background: 'var(--input-area-bg)',
          display: 'flex',
          gap: '8px',
          flexShrink: 0,
        }}>
          <button
            id="delete-all-sessions-btn"
            className="delete-all-btn"
            onClick={handleDeleteAll}
            title="Supprimer toutes les conversations"
            style={{
              flex: 1,
              padding: '4px 6px',
              fontSize: '11px',
              cursor: 'pointer',
              borderRadius: '4px',
              transition: 'all 0.2s',
              fontWeight: '400',
              background: 'var(--delete-all-btn-bg)',
              color: 'var(--delete-all-btn-text)',
              border: '1px solid var(--delete-all-btn-border)',
            }}
          >
            🗑️ Tout supprimer
          </button>
          <button
            id="sidebar-settings-btn"
            className="sidebar-settings-btn"
            onClick={() => setShowSettings(!showSettings)}
            title="Paramètres des couleurs"
            style={{
              flex: 1,
              padding: '4px 6px',
              fontSize: '11px',
              cursor: 'pointer',
              borderRadius: '4px',
              transition: 'all 0.2s',
              fontWeight: '400',
              background: 'var(--settings-btn-bg)',
              color: 'var(--settings-btn-text)',
              border: '1px solid var(--settings-btn-border)',
            }}
          >
            ⚙️ Couleurs
          </button>
        </div>
      </div>

      <AppearanceSettings isOpen={showSettings} onClose={() => setShowSettings(false)} />

      <ConfirmModal
        isOpen={showConfirm}
        message={confirmMessage}
        onConfirm={() => {
          if (confirmCallback) confirmCallback()
          setShowConfirm(false)
        }}
        onCancel={() => setShowConfirm(false)}
      />
    </>
  )
}

