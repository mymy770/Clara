import React, { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../api'
import DetailsPanel from './DetailsPanel'

export default function ChatPanel({ sessionId, messages, onNewMessage, debugEnabled, onSendMessage, isThinking }) {
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef(null)

  function handleQuickActionButton(type) {
    const templates = {
      note: 'Crée une note : ',
      todo: 'Ajoute un todo : ',
      process: 'Crée un process structuré pour : ',
      protocol: 'Crée un protocole pour : '
    }

    const template = templates[type] || ''
    setInput(template)
    
    // Focus sur le textarea
    setTimeout(() => {
      const textarea = document.querySelector('textarea')
      if (textarea) {
        textarea.focus()
        textarea.setSelectionRange(template.length, template.length)
      }
    }, 0)
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  function scrollToBottom() {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  async function handleSend() {
    if (!input.trim() || sending) return

    const userMessage = input.trim()
    setInput('')
    setSending(true)

    // Si onSendMessage est fourni (depuis App), l'utiliser
    if (onSendMessage) {
      onSendMessage(userMessage)
      setSending(false)
      return
    }

    // Sinon, utiliser la logique interne
    // Ajouter le message utilisateur immédiatement
    onNewMessage({ role: 'user', content: userMessage })

    try {
      const response = await sendMessage(userMessage, sessionId, debugEnabled)
      
      // Ajouter la réponse de Clara
      onNewMessage({
        role: 'assistant',
        content: response.reply,
        debug: response.debug,
      })
    } catch (error) {
      console.error('Error sending message:', error)
      onNewMessage({
        role: 'assistant',
        content: `Erreur: ${error.message}`,
      })
    } finally {
      setSending(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-area">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--textSecondary)',
            fontSize: '16px',
            fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
          }}>
            Commencez une conversation avec Clara...
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                marginBottom: '16px',
              }}
            >
              <div
              style={{
                maxWidth: '70%',
                padding: '12px 16px',
                background: msg.role === 'user' ? 'var(--messageUserBg)' : 'var(--messageClaraBg)',
                borderRadius: '18px',
                color: msg.role === 'user' ? 'var(--messageUserText)' : 'var(--messageClaraText)',
                fontSize: '14px',
                lineHeight: '1.5',
                whiteSpace: 'pre-wrap',
                wordWrap: 'break-word',
                boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
              }}
              >
                {msg.content}
                {msg.timestamp && (
                  <div style={{
                    fontSize: '11px',
                    color: msg.role === 'user' ? 'rgba(255,255,255,0.7)' : 'var(--textSecondary)',
                    marginTop: '8px',
                  }}>
                    {msg.timestamp}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Panneau Détails (visible uniquement si debugEnabled) */}
      {debugEnabled && (
        <DetailsPanel 
          debugData={messages[messages.length - 1]?.debug || null}
          isThinking={isThinking}
        />
      )}

      <div className="message-input-area">
        <div style={{ display: 'flex', gap: '8px' }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Tapez votre message... (Enter pour envoyer, Shift+Enter pour nouvelle ligne)"
            disabled={sending}
            style={{
              flex: 1,
              padding: '12px 16px',
              background: 'var(--inputBg)',
              color: 'var(--textPrimary)',
              border: '1px solid var(--borderSubtle)',
              borderRadius: '18px',
              fontSize: '14px',
              fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
              resize: 'none',
              minHeight: '50px',
              maxHeight: '150px',
              transition: 'all 0.2s',
            }}
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            style={{
              padding: '12px 24px',
              background: sending || !input.trim() ? 'var(--borderSubtle)' : 'var(--accent)',
              color: sending || !input.trim() ? 'var(--textSecondary)' : 'var(--textPrimary)',
              border: 'none',
              borderRadius: '18px',
              cursor: sending || !input.trim() ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
              transition: 'all 0.2s',
            }}
          >
            {sending ? '...' : 'Envoyer'}
          </button>
        </div>
      </div>
    </div>
  )
}

