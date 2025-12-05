import React, { useState, useEffect } from 'react'
import SessionSidebarV2 from './components/SessionSidebarV2'
import ChatArea from './components/ChatArea'
import RightPanel from './components/RightPanel'
import { loadSession, sendMessage } from './api'
import { loadThemeFromLocalStorage, applyThemeToDocument } from './config/themeManager'

export default function App() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [isThinking, setIsThinking] = useState(false)
  const [rightPanelOpen, setRightPanelOpen] = useState(true)

  // Charger le thème au démarrage
  useEffect(() => {
    const theme = loadThemeFromLocalStorage()
    applyThemeToDocument(theme)
  }, [])

  function handleNewSession() {
    setSessionId(null)
    setMessages([])
  }

  async function handleSelectSession(sessionIdToLoad) {
    try {
      const sessionData = await loadSession(sessionIdToLoad)
      setSessionId(sessionData.session_id)
      
      // Convertir les messages au format attendu
      const formattedMessages = (sessionData.messages || []).map(msg => ({
        role: msg.role,
        content: msg.content || msg.text || '',
        timestamp: msg.timestamp || new Date().toISOString(),
      }))
      setMessages(formattedMessages)
    } catch (error) {
      console.error('Error loading session:', error)
      alert(`Erreur lors du chargement de la session: ${error.message}`)
    }
  }

  function handleNewMessage(message) {
    setMessages((prev) => [...prev, message])
    
    // Mettre à jour l'état thinking
    if (message.role === 'user') {
      setIsThinking(true)
    } else {
      setIsThinking(false)
    }
  }

  async function handleSendMessage(message) {
    // Ajouter le message utilisateur immédiatement
    handleNewMessage({ 
      role: 'user', 
      content: message,
      timestamp: new Date().toISOString(),
    })
    setIsThinking(true)

    try {
      const response = await sendMessage(message, sessionId, false)
      
      // Le backend peut retourner tous les messages ou juste la réponse
      if (response.messages && Array.isArray(response.messages)) {
        // Format avec tous les messages
        const formattedMessages = response.messages.map(msg => ({
          role: msg.role,
          content: msg.content || msg.text || '',
          timestamp: msg.timestamp || new Date().toISOString(),
        }))
        setMessages(formattedMessages)
      } else {
        // Format avec juste la réponse
        handleNewMessage({
          role: 'assistant',
          content: response.reply || response.content || '',
          timestamp: new Date().toISOString(),
        })
      }
      
      // Mettre à jour sessionId si fourni
      if (response.session_id) {
        setSessionId(response.session_id)
      }
    } catch (error) {
      console.error('Error:', error)
      handleNewMessage({
        role: 'assistant',
        content: `Erreur: ${error.message}`,
        timestamp: new Date().toISOString(),
      })
    }
  }

  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      overflow: 'hidden',
      fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
    }}>
      {/* Sidebar gauche */}
      <SessionSidebarV2
        currentSessionId={sessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
      />

      {/* Zone centrale (Chat) */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
      }}>
        {/* Header avec bouton Todo */}
        <div className="chat-header" style={{
          padding: '10px',
          borderBottom: '1px solid var(--header-border)',
          fontSize: '14px',
          fontWeight: '600',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'var(--header-bg)',
          color: 'var(--header-text)',
          flexShrink: 0,
          zIndex: 1,
        }}>
          <span id="chat-title">
            {sessionId ? (sessionId.replace(/\.txt$/, '') || 'Session') : 'Aucune session'}
          </span>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: '6px', alignItems: 'center' }}>
            <button
              className="toggle-right-panel"
              onClick={() => setRightPanelOpen(!rightPanelOpen)}
              title="Afficher/Masquer Todo & Process"
              style={{
                padding: '4px 10px',
                background: 'var(--todo-btn-bg)',
                color: 'var(--todo-btn-text)',
                border: '1px solid var(--todo-btn-border)',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: '500',
                transition: 'all 0.2s ease',
                minWidth: '50px',
              }}
            >
              Todo
            </button>
          </div>
        </div>

        {/* ChatArea */}
        <ChatArea
          sessionId={sessionId}
          messages={messages}
          onNewMessage={handleNewMessage}
          onSendMessage={handleSendMessage}
          isThinking={isThinking}
        />
      </div>

      {/* Panneau droit (Todo/Process/Think) */}
      <RightPanel
        sessionId={sessionId}
        isOpen={rightPanelOpen}
        onToggle={() => setRightPanelOpen(!rightPanelOpen)}
      />
    </div>
  )
}
