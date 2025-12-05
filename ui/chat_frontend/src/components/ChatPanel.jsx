import React, { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../api'

export default function ChatPanel({ sessionId, messages, onNewMessage, debugEnabled }) {
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef(null)

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

