import React, { useState, useEffect } from 'react'
import SessionSidebarV2 from './components/SessionSidebarV2'
import ChatArea from './components/ChatArea'
import RightPanel from './components/RightPanel'
import InternalPanel from './components/InternalPanel'
import { loadSession, sendMessage } from './api'
import { loadThemeFromLocalStorage, applyThemeToDocument } from './config/themeManager'

export default function App() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [isThinking, setIsThinking] = useState(false)
  const [rightPanelOpen, setRightPanelOpen] = useState(true)
  const [internalPanelOpen, setInternalPanelOpen] = useState(false)
  const [internalThoughts, setInternalThoughts] = useState(null)
  const [internalTodo, setInternalTodo] = useState(null)
  const [internalSteps, setInternalSteps] = useState(null)
  const [useAutogen, setUseAutogen] = useState(false) // Toggle mode Autogen

  // Charger le thème au démarrage
  useEffect(() => {
    try {
      const theme = loadThemeFromLocalStorage()
      applyThemeToDocument(theme)
    } catch (error) {
      console.error('Error loading theme:', error)
    }
  }, [])

  // Debug
  useEffect(() => {
    console.log('App rendered', { sessionId, messagesCount: messages.length, rightPanelOpen })
  }, [sessionId, messages.length, rightPanelOpen])

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
      const response = await sendMessage(message, sessionId, false, useAutogen)
      
      // Extraire les données internes
      const internal = response.internal || {}
      setInternalThoughts(internal.thoughts || null)
      setInternalTodo(internal.todo || null)
      setInternalSteps(internal.steps || null)
      
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
      width: '100%',
      height: '100vh',
      overflow: 'hidden',
      fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
      background: 'var(--main-bg)',
      color: 'var(--text-color)',
    }}>
      {/* Sidebar gauche */}
      <SessionSidebarV2
        currentSessionId={sessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        useAutogen={useAutogen}
        onToggleAutogen={setUseAutogen}
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
            Clara • gpt-5.1
            {sessionId && (
              <span style={{ marginLeft: '12px', opacity: 0.7, fontWeight: '400' }}>
                • {sessionId.replace(/\.txt$/, '') || 'Session'}
              </span>
            )}
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
            {!rightPanelOpen && (
              <button
                onClick={() => setInternalPanelOpen(!internalPanelOpen)}
                title="Afficher/Masquer Détails internes"
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
                }}
              >
                Détails
              </button>
            )}
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

      {/* Panneau Détails internes (visible si RightPanel fermé) */}
      {!rightPanelOpen && (
        <InternalPanel
          thoughts={internalThoughts}
          todo={internalTodo}
          steps={internalSteps}
          open={internalPanelOpen}
          onToggle={() => setInternalPanelOpen(!internalPanelOpen)}
        />
      )}
    </div>
  )
}
