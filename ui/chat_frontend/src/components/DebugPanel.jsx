import React from 'react'

export default function DebugPanel({ debugData }) {
  if (!debugData) {
    return (
      <div className="sidebar right">
        <div style={{ padding: '16px', color: 'var(--text-muted)', textAlign: 'center' }}>
          Activez le mode debug pour voir les informations de débogage
        </div>
      </div>
    )
  }

  return (
    <div className="sidebar right">
      <div style={{ padding: '16px', borderBottom: '1px solid var(--border-subtle)' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '600', margin: 0, color: 'var(--text-main)' }}>
          Debug Info
        </h3>
      </div>
      
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        <pre style={{
          background: 'var(--bg-soft)',
          padding: '12px',
          borderRadius: 'var(--radius-sm)',
          fontSize: '12px',
          color: 'var(--text-main)',
          overflow: 'auto',
          fontFamily: 'monospace',
          whiteSpace: 'pre-wrap',
          wordWrap: 'break-word',
        }}>
          {JSON.stringify(debugData, null, 2)}
        </pre>
      </div>
    </div>
  )
}

