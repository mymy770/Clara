import React, { useState, useRef, useEffect } from 'react'
import { themes } from '../config/theme'

export default function HeaderBar({ onToggleDebug, debugEnabled, onToggleTheme, theme, isThinking, setTheme }) {
  const [showThemeMenu, setShowThemeMenu] = useState(false)
  const themeMenuRef = useRef(null)

  // Fermer le menu si on clique ailleurs
  useEffect(() => {
    function handleClickOutside(event) {
      if (themeMenuRef.current && !themeMenuRef.current.contains(event.target)) {
        setShowThemeMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="header-bar" style={{
      padding: '16px 24px',
      borderBottom: '1px solid var(--borderSubtle)',
      background: 'var(--chatBg)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <h1 style={{ 
          fontSize: '20px', 
          fontWeight: '600', 
          margin: 0,
          color: 'var(--textPrimary)',
          fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
        }}>
          Clara
        </h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Indicateur réflexion animé */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            {isThinking ? (
              <>
                <span style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: 'var(--accent)',
                  animation: 'pulse 1.5s ease-in-out infinite',
                }} />
                <span style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: 'var(--accent)',
                  animation: 'pulse 1.5s ease-in-out infinite 0.2s',
                }} />
                <span style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: 'var(--accent)',
                  animation: 'pulse 1.5s ease-in-out infinite 0.4s',
                }} />
              </>
            ) : (
              <span style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: '#10b981',
                boxShadow: '0 0 8px #10b981',
              }} />
            )}
          </div>
          <span style={{ 
            color: 'var(--textSecondary)', 
            fontSize: '14px',
            fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
          }}>
            {isThinking ? 'En réflexion...' : '● Prête'}
          </span>
          <span style={{ 
            color: 'var(--textSecondary)', 
            fontSize: '12px', 
            marginLeft: '8px',
            opacity: 0.7,
          }}>
            gpt-5.1
          </span>
        </div>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          onClick={onToggleDebug}
          style={{
            padding: '8px 16px',
            background: debugEnabled ? 'var(--accent)' : 'transparent',
            color: debugEnabled ? 'var(--textPrimary)' : 'var(--textSecondary)',
            border: '1px solid var(--borderSubtle)',
            borderRadius: '12px',
            cursor: 'pointer',
            fontSize: '14px',
            fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
            transition: 'all 0.2s',
          }}
        >
          {debugEnabled ? 'Debug ON' : 'Debug OFF'}
        </button>
        
        <div ref={themeMenuRef} style={{ position: 'relative' }}>
          <button
            onClick={() => setShowThemeMenu(!showThemeMenu)}
            style={{
              padding: '8px 16px',
              background: 'transparent',
              color: 'var(--textSecondary)',
              border: '1px solid var(--borderSubtle)',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '14px',
              fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
              transition: 'all 0.2s',
            }}
          >
            Thème
          </button>
          
          {showThemeMenu && (
            <div style={{
              position: 'absolute',
              top: '100%',
              right: 0,
              marginTop: '8px',
              background: 'var(--sidebarBg)',
              border: '1px solid var(--borderSubtle)',
              borderRadius: '12px',
              boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
              minWidth: '180px',
              zIndex: 1000,
            }}>
              {Object.entries(themes).map(([key, themeData]) => (
                <button
                  key={key}
                  onClick={() => {
                    setTheme(key)
                    setShowThemeMenu(false)
                  }}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    background: theme === key ? 'var(--accent)' : 'transparent',
                    color: theme === key ? 'var(--textPrimary)' : 'var(--textSecondary)',
                    border: 'none',
                    borderRadius: theme === key ? '12px' : '0',
                    cursor: 'pointer',
                    fontSize: '14px',
                    textAlign: 'left',
                    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
                    transition: 'all 0.2s',
                  }}
                >
                  {themeData.name}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(0.8); }
        }
      `}</style>
    </div>
  )
}

