import React, { useState } from 'react'
import { sendMessage } from '../api'

export default function MemoryToolsPanel({ sessionId, onSendMessage, onNewMessage }) {
  const [deepThinking, setDeepThinking] = useState(false)
  const [autoSaveNotes, setAutoSaveNotes] = useState(false)
  const [autoUseMemory, setAutoUseMemory] = useState(false)

  async function handleMemoryAction(type) {
    const commands = {
      note: 'Montre-moi toutes mes notes',
      todo: 'Montre-moi tous mes todos',
      process: 'Montre-moi tous mes process',
      protocol: 'Montre-moi tous mes protocoles',
      preference: 'Montre-moi toutes mes préférences',
      contact: 'Montre-moi tous mes contacts'
    }

    const message = commands[type] || `Liste mes ${type}s`
    
    // Envoyer le message
    if (onSendMessage) {
      onSendMessage(message)
    } else {
      // Fallback : appeler directement l'API
      try {
        const response = await sendMessage(message, sessionId, false)
        onNewMessage({
          role: 'assistant',
          content: response.reply,
        })
      } catch (error) {
        console.error('Error:', error)
      }
    }
  }

  function handleQuickAction(action) {
    const templates = {
      reformuler: 'Reformule ceci de manière plus claire : ',
      resumer: 'Résume ceci en quelques points clés : ',
      brainstorm: 'Fais un brainstorming sur : '
    }

    const template = templates[action] || ''
    if (onSendMessage) {
      onSendMessage(template)
    }
  }

  return (
    <div className="sidebar right" style={{
      background: 'var(--bg-panel)',
      borderLeft: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* Section Mémoire */}
      <div style={{ padding: '16px', borderBottom: '1px solid var(--border-subtle)' }}>
        <h3 style={{
          fontSize: '14px',
          fontWeight: '600',
          color: 'var(--text-primary)',
          marginBottom: '12px',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
        }}>
          Mémoire
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {['note', 'todo', 'process', 'protocol', 'preference', 'contact'].map((type) => (
            <button
              key={type}
              onClick={() => handleMemoryAction(type)}
              style={{
                padding: '10px 12px',
                background: 'var(--bg-soft)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                fontSize: '13px',
                textAlign: 'left',
                fontFamily: 'var(--font-sans)',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'var(--accent-soft)'
                e.target.style.borderColor = 'var(--accent)'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'var(--bg-soft)'
                e.target.style.borderColor = 'var(--border-subtle)'
              }}
            >
              Voir mes {type}s
            </button>
          ))}
        </div>
      </div>

      {/* Section Quick Actions */}
      <div style={{ padding: '16px', borderBottom: '1px solid var(--border-subtle)' }}>
        <h3 style={{
          fontSize: '14px',
          fontWeight: '600',
          color: 'var(--text-primary)',
          marginBottom: '12px',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
        }}>
          Actions rapides
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {['reformuler', 'resumer', 'brainstorm'].map((action) => (
            <button
              key={action}
              onClick={() => handleQuickAction(action)}
              style={{
                padding: '10px 12px',
                background: 'var(--bg-soft)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                fontSize: '13px',
                textAlign: 'left',
                fontFamily: 'var(--font-sans)',
                textTransform: 'capitalize',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'var(--accent-soft)'
                e.target.style.borderColor = 'var(--accent)'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'var(--bg-soft)'
                e.target.style.borderColor = 'var(--border-subtle)'
              }}
            >
              {action}
            </button>
          ))}
        </div>
      </div>

      {/* Section Modes */}
      <div style={{ padding: '16px', flex: 1, overflowY: 'auto' }}>
        <h3 style={{
          fontSize: '14px',
          fontWeight: '600',
          color: 'var(--text-primary)',
          marginBottom: '12px',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
        }}>
          Modes
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {[
            { key: 'deepThinking', label: 'Mode réflexion profonde' },
            { key: 'autoSaveNotes', label: 'Sauvegarde auto notes' },
            { key: 'autoUseMemory', label: 'Utilisation auto mémoire' }
          ].map(({ key, label }) => {
            const value = key === 'deepThinking' ? deepThinking : 
                         key === 'autoSaveNotes' ? autoSaveNotes : autoUseMemory
            const setter = key === 'deepThinking' ? setDeepThinking :
                          key === 'autoSaveNotes' ? setAutoSaveNotes : setAutoUseMemory

            return (
              <div key={key} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <label style={{ fontSize: '13px', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                  {label}
                </label>
                <button
                  onClick={() => setter(!value)}
                  style={{
                    width: '44px',
                    height: '24px',
                    background: value ? 'var(--accent)' : 'var(--bg-soft)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-button)',
                    cursor: 'pointer',
                    position: 'relative',
                    transition: 'all 0.2s',
                  }}
                >
                  <div style={{
                    width: '18px',
                    height: '18px',
                    background: 'var(--text-primary)',
                    borderRadius: '50%',
                    position: 'absolute',
                    top: '2px',
                    left: value ? '22px' : '2px',
                    transition: 'left 0.2s',
                  }} />
                </button>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

