import React, { useState, useEffect } from 'react'
import HeaderBar from './components/HeaderBar'
import SessionSidebar from './components/SessionSidebar'
import ChatPanel from './components/ChatPanel'
import DebugPanel from './components/DebugPanel'
import MemoryToolsPanel from './components/MemoryToolsPanel'
import { loadSession, sendMessage } from './api'
import layoutConfig from './config/layout.json'

export default function App() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [debugEnabled, setDebugEnabled] = useState(false)
  const [debugData, setDebugData] = useState(null)
  const [theme, setTheme] = useState('dark')
  const [layout, setLayout] = useState(layoutConfig)
  const [isThinking, setIsThinking] = useState(false)
  const [showRightPanel, setShowRightPanel] = useState(layoutConfig.layout?.showRightPanel || true)

  // Appliquer le layout depuis la config
  useEffect(() => {
    const sidebarLeftWidth = layout.layout?.sidebarLeftWidth || 280
    const sidebarRightWidth = layout.layout?.sidebarRightWidth || 320
    document.documentElement.style.setProperty('--left-sidebar-width', `${sidebarLeftWidth}px`)
    document.documentElement.style.setProperty('--right-sidebar-width', `${sidebarRightWidth}px`)
    document.documentElement.style.setProperty('--chat-min-width', layout.chatMinWidth || '480px')
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
    
    // Mettre à jour l'état thinking
    if (message.role === 'user') {
      setIsThinking(true)
    } else {
      setIsThinking(false)
    }
  }

  async function handleSendMessage(message) {
    // Ajouter le message utilisateur immédiatement
    handleNewMessage({ role: 'user', content: message })
    setIsThinking(true)

    try {
      const response = await sendMessage(message, sessionId, debugEnabled)
      handleNewMessage({
        role: 'assistant',
        content: response.reply,
        debug: response.debug,
      })
    } catch (error) {
      console.error('Error:', error)
      handleNewMessage({
        role: 'assistant',
        content: `Erreur: ${error.message}`,
      })
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
  const showLeft = layout.layout?.showSessions !== false
  const showRight = showRightPanel && (layout.layout?.showMemoryPanel !== false)
  
  const appClasses = [
    'app-root',
    showLeft ? 'with-left-sidebar' : '',
    showRight ? 'with-right-sidebar' : '',
  ].filter(Boolean).join(' ')

  return (
    <div className={appClasses}>
      {showLeft && (
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
          isThinking={isThinking}
        />
        <ChatPanel
          sessionId={sessionId}
          messages={messages}
          onNewMessage={handleNewMessage}
          debugEnabled={debugEnabled}
          onSendMessage={handleSendMessage}
        />
      </div>
      
      {showRight && !debugEnabled && (
        <MemoryToolsPanel
          sessionId={sessionId}
          onSendMessage={handleSendMessage}
          onNewMessage={handleNewMessage}
        />
      )}
      
      {debugEnabled && (
        <DebugPanel debugData={debugData} />
      )}
    </div>
  )
}

