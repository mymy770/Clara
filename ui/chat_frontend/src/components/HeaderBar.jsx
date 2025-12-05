import React from 'react'

export default function HeaderBar({ onToggleDebug, debugEnabled, onToggleTheme, theme }) {
  return (
    <div className="header-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <h1 style={{ fontSize: '20px', fontWeight: '600', margin: 0 }}>Clara</h1>
        <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Assistant IA</span>
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

