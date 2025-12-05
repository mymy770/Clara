import React, { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../api'

export default function ChatPanel({ sessionId, messages, onNewMessage, debugEnabled, onQuickAction }) {
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
            color: 'var(--text-muted)',
            fontSize: '16px',
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
                  background: msg.role === 'user' ? 'var(--accent)' : 'var(--bg-elevated)',
                  borderRadius: msg.role === 'user' ? 'var(--radius-md) var(--radius-md) var(--radius-md) 0' : 'var(--radius-md) var(--radius-md) 0 var(--radius-md)',
                  color: 'var(--text-main)',
                  fontSize: '14px',
                  lineHeight: '1.5',
                  whiteSpace: 'pre-wrap',
                  wordWrap: 'break-word',
                }}
              >
                {msg.content}
                {msg.timestamp && (
                  <div style={{
                    fontSize: '11px',
                    color: 'var(--text-muted)',
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

      <div className="message-input-area">
        {/* Quick action buttons */}
        <div style={{ display: 'flex', gap: '6px', marginBottom: '8px', flexWrap: 'wrap' }}>
          {['note', 'todo', 'process', 'protocol'].map((type) => (
            <button
              key={type}
              onClick={() => handleQuickActionButton(type)}
              style={{
                padding: '6px 12px',
                background: 'var(--bg-soft)',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                fontSize: '12px',
                fontFamily: 'var(--font-sans)',
                textTransform: 'capitalize',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'var(--accent-soft)'
                e.target.style.color = 'var(--text-primary)'
                e.target.style.borderColor = 'var(--accent)'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'var(--bg-soft)'
                e.target.style.color = 'var(--text-secondary)'
                e.target.style.borderColor = 'var(--border-subtle)'
              }}
            >
              {type}
            </button>
          ))}
        </div>
        
        <div style={{ display: 'flex', gap: '8px' }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Tapez votre message... (Enter pour envoyer, Shift+Enter pour nouvelle ligne)"
            disabled={sending}
            style={{
              flex: 1,
              padding: '12px',
              background: 'var(--bg-soft)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              fontSize: '14px',
              fontFamily: 'var(--font-sans)',
              resize: 'none',
              minHeight: '50px',
              maxHeight: '150px',
            }}
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            style={{
              padding: '12px 24px',
              background: sending || !input.trim() ? 'var(--bg-soft)' : 'var(--accent)',
              color: 'var(--text-main)',
              border: 'none',
              borderRadius: 'var(--radius-sm)',
              cursor: sending || !input.trim() ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              fontFamily: 'var(--font-sans)',
            }}
          >
            {sending ? '...' : 'Envoyer'}
          </button>
        </div>
      </div>
    </div>
  )
}

