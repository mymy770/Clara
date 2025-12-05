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

          // Ajouter la ponctuation automatique et capitalisation
          if (finalTranscript) {
            // Ajouter un espace avant si nécessaire
            if (baseInput && !baseInput.endsWith(' ') && !baseInput.endsWith('\n')) {
              baseInput += ' '
            }
            // Traiter le texte final
            let text = finalTranscript.trim()
            
            if (text) {
              // Capitaliser la première lettre
              text = text.charAt(0).toUpperCase() + text.slice(1)
              
              // Détecter si c'est une question
              const isQuestion = detectQuestion(text)
              
              // Ajouter la ponctuation appropriée
              if (!/[.!?]$/.test(text)) {
                text += isQuestion ? '?' : '.'
              }
            }
            
            baseInput += text + ' '
          }

          // Traiter le texte intermédiaire avec capitalisation
          let displayText = baseInput
          if (interimTranscript) {
            let interim = interimTranscript.trim()
            if (interim) {
              // Capitaliser la première lettre du texte intermédiaire si c'est le début d'une phrase
              if (!baseInput || baseInput.trim().endsWith('.') || baseInput.trim().endsWith('?') || baseInput.trim().endsWith('!')) {
                interim = interim.charAt(0).toUpperCase() + interim.slice(1)
              }
              displayText += interim
            }
          }

          // Afficher base + interim
          setInput(displayText)
        }
        
        // Fonction pour détecter si c'est une question
        function detectQuestion(text) {
          const lowerText = text.toLowerCase().trim()
          
          // Mots interrogatifs au début
          const questionStarters = [
            'est-ce que', 'est ce que', 'qu\'est-ce que', 'qu est ce que',
            'comment', 'pourquoi', 'quand', 'où', 'qui', 'quoi', 'quel', 'quelle', 'quels', 'quelles',
            'combien', 'lequel', 'laquelle', 'lesquels', 'lesquelles',
            'peux-tu', 'peux tu', 'peut-on', 'peut on', 'peut-il', 'peut il',
            'as-tu', 'as tu', 'avez-vous', 'avez vous', 'es-tu', 'es tu', 'êtes-vous', 'êtes vous'
          ]
          
          // Vérifier si ça commence par un mot interrogatif
          for (const starter of questionStarters) {
            if (lowerText.startsWith(starter + ' ') || lowerText === starter) {
              return true
            }
          }
          
          // Vérifier si ça se termine par une intonation montante (approximation)
          // Les phrases courtes qui se terminent par certains mots peuvent être des questions
          const questionEnders = ['n\'est-ce pas', 'n est ce pas', 'non', 'si', 'hein', 'd\'accord', 'd accord']
          for (const ender of questionEnders) {
            if (lowerText.endsWith(' ' + ender) || lowerText.endsWith(ender)) {
              return true
            }
          }
          
          // Détecter l'intonation via la structure (approximation)
          // Si la phrase est courte et se termine par certains patterns
          if (text.length < 50) {
            // Patterns de questions courantes
            if (/\b(c\'est|ce sont|il est|elle est|ils sont|elles sont)\b/i.test(text) && text.length < 30) {
              return true
            }
          }
          
          return false
        }

        recognition.onerror = (event) => {
          console.error('Erreur reconnaissance vocale:', event.error)
          // Ne pas arrêter automatiquement, seulement si erreur fatale
          if (event.error === 'no-speech' || event.error === 'aborted') {
            // Ignorer ces erreurs, continuer l'enregistrement
            return
          }
          shouldContinueRef.current = false
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
            outline: 'none',
            transition: 'border-color 0.2s',
          }}
          onFocus={(e) => {
            e.target.style.borderColor = 'var(--input-focus-border)'
          }}
          onBlur={(e) => {
            e.target.style.borderColor = 'var(--input-border)'
          }}
        />
        <button
          id="mic-btn"
          onClick={toggleListening}
          disabled={sending}
          title={isListening ? 'Arrêter l\'enregistrement' : 'Parler'}
          style={{
            padding: '8px',
            cursor: sending ? 'not-allowed' : 'pointer',
            border: '1px solid var(--mic-btn-border)',
            borderRadius: '6px',
            background: 'var(--mic-btn-bg)',
            color: 'var(--mic-btn-text)',
            transition: 'all 0.2s',
            opacity: sending ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minWidth: '36px',
            minHeight: '36px',
            ...(isListening && {
              border: '1px solid var(--mic-btn-active-border)',
              background: 'var(--mic-btn-active-bg)',
              color: 'var(--mic-btn-active-text)',
            }),
          }}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            style={{ display: 'block' }}
          >
            <path
              d="M8 1C7.17157 1 6.5 1.67157 6.5 2.5V8C6.5 8.82843 7.17157 9.5 8 9.5C8.82843 9.5 9.5 8.82843 9.5 8V2.5C9.5 1.67157 8.82843 1 8 1Z"
              fill="currentColor"
            />
            <path
              d="M4 7C4 6.44772 3.55228 6 3 6C2.44772 6 2 6.44772 2 7C2 9.76142 4.23858 12 7 12V13H5C4.44772 13 4 13.4477 4 14C4 14.5523 4.44772 15 5 15H11C11.5523 15 12 14.5523 12 14C12 13.4477 11.5523 13 11 13H9V12C11.7614 12 14 9.76142 14 7C14 6.44772 13.5523 6 13 6C12.4477 6 12 6.44772 12 7C12 9.20914 10.2091 11 8 11C5.79086 11 4 9.20914 4 7Z"
              fill="currentColor"
            />
          </svg>
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

