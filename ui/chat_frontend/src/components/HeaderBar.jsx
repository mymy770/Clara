import React from 'react'

export default function HeaderBar({ onToggleDebug, debugEnabled, onToggleTheme, theme, isThinking }) {
  return (
    <div className="header-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <h1 style={{ fontSize: '20px', fontWeight: '600', margin: 0 }}>Clara</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: isThinking ? '#fbbf24' : '#10b981',
            boxShadow: isThinking ? '0 0 8px #fbbf24' : '0 0 8px #10b981',
          }} />
          <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
            {isThinking ? 'Réflexion...' : 'Prête'}
          </span>
          <span style={{ color: 'var(--text-subtle)', fontSize: '12px', marginLeft: '8px' }}>
            gpt-5.1
          </span>
        </div>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          onClick={onToggleDebug}
          style={{
            padding: '8px 16px',
            background: debugEnabled ? 'var(--accent)' : 'var(--bg-soft)',
            color: 'var(--text-main)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            fontSize: '14px',
            fontFamily: 'var(--font-sans)',
          }}
        >
          {debugEnabled ? 'Debug ON' : 'Debug OFF'}
        </button>
        
        <button
          onClick={onToggleTheme}
          style={{
            padding: '8px 16px',
            background: 'var(--bg-soft)',
            color: 'var(--text-main)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            fontSize: '14px',
            fontFamily: 'var(--font-sans)',
          }}
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
      </div>
    </div>
  )
}

