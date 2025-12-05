import React, { useState, useEffect } from 'react'
import HeaderBar from './components/HeaderBar'
import SessionSidebar from './components/SessionSidebar'
import ChatPanel from './components/ChatPanel'
import DebugPanel from './components/DebugPanel'
import { loadSession } from './api'
import layoutConfig from './config/layout.json'

export default function App() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [debugEnabled, setDebugEnabled] = useState(false)
  const [debugData, setDebugData] = useState(null)
  const [theme, setTheme] = useState('dark')
  const [layout, setLayout] = useState(layoutConfig)

  // Appliquer le layout depuis la config
  useEffect(() => {
    document.documentElement.style.setProperty('--left-sidebar-width', layout.leftSidebarWidth)
    document.documentElement.style.setProperty('--right-sidebar-width', layout.rightSidebarWidth)
    document.documentElement.style.setProperty('--chat-min-width', layout.chatMinWidth)
    document.documentElement.className = `theme-${theme}`
  }, [layout, theme])

  function handleNewSession() {
    setSessionId(null)
    setMessages([])
    setDebugData(null)
  }

  async function handleSelectSession(sessionIdToLoad) {
    try {
      const sessionData = await loadSession(sessionIdToLoad)
      setSessionId(sessionData.session_id)
      setMessages(sessionData.messages || [])
    } catch (error) {
      console.error('Error loading session:', error)
      alert(`Erreur lors du chargement de la session: ${error.message}`)
    }
  }

  function handleNewMessage(message) {
    setMessages((prev) => [...prev, message])
    
    // Extraire les données de debug si présentes
    if (message.debug) {
      setDebugData(message.debug)
    }
  }

  function handleToggleDebug() {
    setDebugEnabled(!debugEnabled)
    if (!debugEnabled) {
      setDebugData(null)
    }
  }

  function handleToggleTheme() {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  // Classes CSS pour le layout
  const appClasses = [
    'app-root',
    layout.showLeftSidebar ? 'with-left-sidebar' : '',
    layout.showRightDebug && debugEnabled ? 'with-right-sidebar' : '',
  ].filter(Boolean).join(' ')

  return (
    <div className={appClasses}>
      {layout.showLeftSidebar && (
        <SessionSidebar
          currentSessionId={sessionId}
          onSelectSession={handleSelectSession}
          onNewSession={handleNewSession}
        />
      )}
      
      <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <HeaderBar
          onToggleDebug={handleToggleDebug}
          debugEnabled={debugEnabled}
          onToggleTheme={handleToggleTheme}
          theme={theme}
        />
        <ChatPanel
          sessionId={sessionId}
          messages={messages}
          onNewMessage={handleNewMessage}
          debugEnabled={debugEnabled}
        />
      </div>
      
      {layout.showRightDebug && debugEnabled && (
        <DebugPanel debugData={debugData} />
      )}
    </div>
  )
}

