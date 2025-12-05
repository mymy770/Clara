import React, { useState } from 'react'

export default function DetailsPanel({ debugData, isThinking }) {
  const [isOpen, setIsOpen] = useState(false)
  const [openSections, setOpenSections] = useState({
    thinking: false,
    steps: false,
    memory: false,
  })

  if (!debugData && !isThinking) {
    return null
  }

  function toggleSection(section) {
    setOpenSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  return (
    <div style={{
      borderTop: '1px solid var(--borderSubtle)',
      background: 'var(--chatBg)',
      transition: 'max-height 0.3s ease',
      maxHeight: isOpen ? '400px' : '40px',
      overflow: 'hidden',
    }}>
      {/* Barre de titre cliquable */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        style={{
          padding: '12px 16px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'var(--sidebarBg)',
          borderBottom: isOpen ? '1px solid var(--borderSubtle)' : 'none',
        }}
      >
        <span style={{
          fontSize: '13px',
          fontWeight: '500',
          color: 'var(--textSecondary)',
        }}>
          Détails (debug)
        </span>
        <span style={{
          fontSize: '12px',
          color: 'var(--textSecondary)',
          transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
          transition: 'transform 0.2s',
        }}>
          ▼
        </span>
      </div>

      {/* Contenu repliable */}
      {isOpen && (
        <div style={{
          padding: '16px',
          maxHeight: '360px',
          overflowY: 'auto',
        }}>
          {/* Section Réflexion */}
          <div style={{ marginBottom: '16px' }}>
            <div
              onClick={() => toggleSection('thinking')}
              style={{
                padding: '8px 12px',
                background: 'var(--sidebarBg)',
                borderRadius: '12px',
                cursor: 'pointer',
                marginBottom: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--textPrimary)' }}>
                🧠 Réflexion
              </span>
              <span style={{ fontSize: '12px', color: 'var(--textSecondary)' }}>
                {openSections.thinking ? '▼' : '▶'}
              </span>
            </div>
            {openSections.thinking && (
              <div style={{
                padding: '12px',
                background: 'var(--sidebarBg)',
                borderRadius: '12px',
                fontSize: '12px',
                color: 'var(--textSecondary)',
                fontFamily: 'monospace',
                whiteSpace: 'pre-wrap',
              }}>
                {isThinking ? 'Clara réfléchit...' : (debugData?.thinking || 'Non disponible')}
              </div>
            )}
          </div>

          {/* Section Étapes / Todo */}
          <div style={{ marginBottom: '16px' }}>
            <div
              onClick={() => toggleSection('steps')}
              style={{
                padding: '8px 12px',
                background: 'var(--sidebarBg)',
                borderRadius: '12px',
                cursor: 'pointer',
                marginBottom: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--textPrimary)' }}>
                ✅ Étapes / Todo
              </span>
              <span style={{ fontSize: '12px', color: 'var(--textSecondary)' }}>
                {openSections.steps ? '▼' : '▶'}
              </span>
            </div>
            {openSections.steps && (
              <div style={{
                padding: '12px',
                background: 'var(--sidebarBg)',
                borderRadius: '12px',
                fontSize: '12px',
                color: 'var(--textSecondary)',
              }}>
                {debugData?.steps ? (
                  <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    {debugData.steps.map((step, idx) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ul>
                ) : (
                  'Pas encore de détails disponibles pour ce message.'
                )}
              </div>
            )}
          </div>

          {/* Section Actions mémoire */}
          <div>
            <div
              onClick={() => toggleSection('memory')}
              style={{
                padding: '8px 12px',
                background: 'var(--sidebarBg)',
                borderRadius: '12px',
                cursor: 'pointer',
                marginBottom: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--textPrimary)' }}>
                💾 Actions mémoire
              </span>
              <span style={{ fontSize: '12px', color: 'var(--textSecondary)' }}>
                {openSections.memory ? '▼' : '▶'}
              </span>
            </div>
            {openSections.memory && (
              <div style={{
                padding: '12px',
                background: 'var(--sidebarBg)',
                borderRadius: '12px',
                fontSize: '12px',
                color: 'var(--textSecondary)',
                fontFamily: 'monospace',
              }}>
                {debugData?.memory_actions ? (
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(debugData.memory_actions, null, 2)}
                  </pre>
                ) : (
                  'Pas encore de détails disponibles pour ce message.'
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

