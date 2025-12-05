import React, { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../api'

export default function ChatArea({ sessionId, messages, onNewMessage, onSendMessage, isThinking }) {
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)
  const recognitionRef = useRef(null)
  const shouldContinueRef = useRef(false)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialiser la reconnaissance vocale
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition()
        recognition.continuous = true  // Continue jusqu'à arrêt manuel
        recognition.interimResults = true
        recognition.lang = 'fr-FR'

        let baseInput = ''
        let lastFinalIndex = 0

        recognition.onstart = () => {
          setIsListening(true)
          shouldContinueRef.current = true
          // Sauvegarder l'input actuel comme base
          setInput(prev => {
            baseInput = prev
            return prev
          })
          lastFinalIndex = 0
        }

        recognition.onresult = (event) => {
          let interimTranscript = ''
          let finalTranscript = ''

          // Traiter seulement les nouveaux résultats depuis le dernier index final
          for (let i = lastFinalIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript
            if (event.results[i].isFinal) {
              finalTranscript += transcript
              lastFinalIndex = i + 1
            } else {
              interimTranscript += transcript
            }
          }

          // Ajouter la ponctuation automatique
          if (finalTranscript) {
            // Ajouter un espace avant si nécessaire
            if (baseInput && !baseInput.endsWith(' ') && !baseInput.endsWith('\n')) {
              baseInput += ' '
            }
            // Ajouter le texte final avec ponctuation
            let text = finalTranscript.trim()
            // Ajouter un point si la phrase ne se termine pas par une ponctuation
            if (text && !/[.!?]$/.test(text)) {
              text += '.'
            }
            baseInput += text + ' '
          }

          // Afficher base + interim (sans ponctuation pour l'instant)
          setInput(baseInput + interimTranscript)
        }

        recognition.onerror = (event) => {
          console.error('Erreur reconnaissance vocale:', event.error)
          // Ne pas arrêter automatiquement, seulement si erreur fatale
          if (event.error === 'no-speech' || event.error === 'aborted') {
            // Ignorer ces erreurs, continuer l'enregistrement
            return
          }
          shouldContinue = false
          setIsListening(false)
        }

        recognition.onend = () => {
          // Ne pas arrêter automatiquement, seulement si l'utilisateur clique
          // Si onend est appelé sans clic utilisateur, relancer (sauf si shouldContinueRef est false)
          if (shouldContinueRef.current) {
            // Relancer automatiquement pour continuer l'enregistrement
            try {
              recognition.start()
            } catch (e) {
              // Si erreur, arrêter proprement
              shouldContinueRef.current = false
              setIsListening(false)
            }
          }
        }

        recognitionRef.current = recognition
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [])

  function scrollToBottom() {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  function formatTime(ts) {
    try {
      if (!ts) return ""
      const d = new Date(ts)
      if (isNaN(d.getTime())) return ""
      return d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })
    } catch (e) {
      return ""
    }
  }

  async function handleSend() {
    if (!input.trim() || sending) return

    const userMessage = input.trim()
    setInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = '40px'
    }

    // Si onSendMessage est fourni (depuis App), l'utiliser
    if (onSendMessage) {
      onSendMessage(userMessage)
      return
    }

    // Sinon, utiliser la logique interne
    setSending(true)
    onNewMessage({ role: 'user', content: userMessage, timestamp: new Date().toISOString() })

    try {
      const response = await sendMessage(userMessage, sessionId, false)
      onNewMessage({
        role: 'assistant',
        content: response.reply,
        timestamp: new Date().toISOString(),
      })
    } catch (error) {
      console.error('Error sending message:', error)
      onNewMessage({
        role: 'assistant',
        content: `Erreur: ${error.message}`,
        timestamp: new Date().toISOString(),
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

  function handleInputChange(e) {
    setInput(e.target.value)
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px'
    }
  }

  function toggleListening() {
    if (!recognitionRef.current) {
      alert('La reconnaissance vocale n\'est pas disponible dans votre navigateur.')
      return
    }

    if (isListening) {
      // Arrêter manuellement
      shouldContinueRef.current = false
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      try {
        shouldContinueRef.current = true
        recognitionRef.current.start()
      } catch (error) {
        console.error('Erreur démarrage reconnaissance:', error)
        shouldContinueRef.current = false
        setIsListening(false)
      }
    }
  }

  return (
    <div className="main" style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      position: 'relative',
      overflow: 'hidden',
      background: 'var(--main-bg)',
    }}>
      <div id="chat" className="chat" style={{
        flex: 1,
        padding: '10px',
        overflowY: 'auto',
        background: 'var(--chat-bg)',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
      }}>
        {messages.length === 0 ? (
          <div style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-color)',
            fontSize: '16px',
          }}>
            Commencez une conversation avec Clara...
          </div>
        ) : (
          messages.map((msg, idx) => {
            const roleKey = (msg.role === 'user' || msg.role === 'jeremy') ? 'jeremy' : 'clara'
            return (
              <div
                key={idx}
                className={`msg ${roleKey === 'jeremy' ? 'user' : 'clara'}`}
                style={{
                  display: 'flex',
                  margin: '6px 0',
                  width: '100%',
                  justifyContent: roleKey === 'jeremy' ? 'flex-end' : 'flex-start',
                }}
              >
                <div
                  className={`bubble ${roleKey === 'jeremy' ? 'bubble-jeremy' : 'bubble-clara'}`}
                  style={{
                    display: 'inline-block',
                    maxWidth: '65%',
                    padding: '8px 12px',
                    margin: 0,
                    borderRadius: '12px',
                    fontSize: 'var(--chat-font-size, 14px)',
                    lineHeight: '1.4',
                    wordWrap: 'break-word',
                    whiteSpace: 'pre-line',
                    border: '1px solid transparent',
                    background: roleKey === 'jeremy' ? 'var(--jeremy-bubble-bg)' : 'var(--clara-bubble-bg)',
                    borderColor: roleKey === 'jeremy' ? 'var(--jeremy-bubble-border)' : 'var(--clara-bubble-border)',
                    color: roleKey === 'jeremy' ? 'var(--jeremy-bubble-text)' : 'var(--clara-bubble-text)',
                  }}
                >
                  <div>{msg.content || ''}</div>
                  {msg.timestamp && (
                    <span className="time" style={{
                      display: 'block',
                      fontSize: '11px',
                      color: 'var(--time-color)',
                      marginTop: '3px',
                      textAlign: 'right',
                    }}>
                      {formatTime(msg.timestamp)}
                    </span>
                  )}
                </div>
              </div>
            )
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="typing" style={{
        fontSize: '11px',
        color: 'var(--time-color)',
        padding: '0 10px 4px',
        fontStyle: 'italic',
        display: isThinking ? 'block' : 'none',
      }}>
        Clara écrit...
      </div>

      <div className="input-area" style={{
        padding: '12px 8px',
        display: 'flex',
        gap: '8px',
        background: 'var(--input-area-bg)',
      }}>
        <textarea
          ref={textareaRef}
          id="message-input"
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Écris à Clara..."
          disabled={sending}
          style={{
            flex: 1,
            resize: 'none',
            minHeight: '40px',
            maxHeight: '120px',
            padding: '8px',
            fontFamily: 'inherit',
            fontSize: '13px',
            border: '1px solid var(--input-border)',
            borderRadius: '6px',
            background: 'var(--input-bg)',
            color: 'var(--input-text)',
          }}
        />
        <button
          id="mic-btn"
          onClick={toggleListening}
          disabled={sending}
          title={isListening ? 'Arrêter l\'enregistrement' : 'Parler'}
          style={{
            padding: '8px 12px',
            fontSize: '18px',
            cursor: sending ? 'not-allowed' : 'pointer',
            border: `1px solid ${isListening ? 'var(--mic-btn-active-border)' : 'var(--mic-btn-border)'}`,
            borderRadius: '6px',
            background: isListening ? 'var(--mic-btn-active-bg)' : 'var(--mic-btn-bg)',
            color: isListening ? 'var(--mic-btn-active-text)' : 'var(--mic-btn-text)',
            transition: 'all 0.2s',
            opacity: sending ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minWidth: '44px',
          }}
        >
          🎤
        </button>
        <button
          id="send-btn"
          onClick={handleSend}
          disabled={!input.trim() || sending}
          style={{
            padding: '8px 16px',
            fontSize: '13px',
            cursor: sending || !input.trim() ? 'not-allowed' : 'pointer',
            border: '1px solid var(--send-btn-border)',
            borderRadius: '6px',
            background: 'var(--send-btn-bg)',
            color: 'var(--send-btn-text)',
            transition: 'all 0.2s',
            opacity: sending || !input.trim() ? 0.5 : 1,
          }}
        >
          Envoyer
        </button>
      </div>
    </div>
  )
}

