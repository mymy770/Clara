import React, { useState, useEffect, useRef } from 'react'
import { getSessionTodos, getSessionLogs, getSessionThinking } from '../api'

export default function RightPanel({ sessionId, isOpen, onToggle }) {
  const [activeTab, setActiveTab] = useState('todo')
  const [todos, setTodos] = useState([])
  const [logs, setLogs] = useState([])
  const [thinking, setThinking] = useState([])
  const thinkContentRef = useRef(null)
  const lastThoughtCountRef = useRef(0)
  const processPollIntervalRef = useRef(null)

  useEffect(() => {
    if (sessionId && isOpen) {
      loadTodos()
      loadProcess()
      loadThinking()
      startPolling()
    } else {
      stopPolling()
    }
    return () => stopPolling()
  }, [sessionId, isOpen])

  function startPolling() {
    if (processPollIntervalRef.current) {
      clearInterval(processPollIntervalRef.current)
    }
    if (!sessionId) return
    
    processPollIntervalRef.current = setInterval(() => {
      loadProcess()
      loadThinking()
    }, 2000)
  }

  function stopPolling() {
    if (processPollIntervalRef.current) {
      clearInterval(processPollIntervalRef.current)
      processPollIntervalRef.current = null
    }
  }

  async function loadTodos() {
    if (!sessionId) {
      setTodos([])
      return
    }
    try {
      const data = await getSessionTodos(sessionId)
      setTodos(data.todos || [])
    } catch (e) {
      // Fallback sur logs si endpoint todos n'existe pas
      try {
        const logData = await getSessionLogs(sessionId)
        const todosFromLogs = (logData.logs || [])
          .filter(log => log.text && (log.text.includes('TODO') || log.text.includes('STEP')))
          .map(log => {
            const text = log.text || ''
            const isDone = text.includes('DONE') || text.includes('COMPLETED')
            return { text, timestamp: log.timestamp, done: isDone }
          })
        setTodos(todosFromLogs)
      } catch (e2) {
        console.error('Error loading todos', e2)
        setTodos([])
      }
    }
  }

  async function loadProcess() {
    if (!sessionId) return
    try {
      const data = await getSessionLogs(sessionId)
      setLogs(data.logs || [])
    } catch (e) {
      console.error('Error loading process', e)
      setLogs([])
    }
  }

  async function loadThinking() {
    if (!sessionId) return
    try {
      const data = await getSessionThinking(sessionId)
      const thoughts = data.thinking || []
      
      // Gérer l'auto-scroll intelligent
      const thinkContent = thinkContentRef.current
      if (thinkContent) {
        const wasNearBottom = thinkContent.scrollHeight - thinkContent.scrollTop - thinkContent.clientHeight < 50
        const hasNewThoughts = thoughts.length > lastThoughtCountRef.current
        lastThoughtCountRef.current = thoughts.length
        
        setThinking(thoughts)
        
        // Auto-scroll seulement si nouvelles pensées et on était en bas
        if (hasNewThoughts && wasNearBottom) {
          setTimeout(() => {
            if (thinkContent) {
              thinkContent.scrollTop = thinkContent.scrollHeight + 20
            }
          }, 150)
        }
      } else {
        setThinking(thoughts)
      }
    } catch (e) {
      console.error('Error loading thinking', e)
      setThinking([])
    }
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

  function escapeHtml(text) {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }

  return (
    <div className={`right-panel ${!isOpen ? 'collapsed' : ''}`} style={{
      width: isOpen ? '320px' : '0',
      borderLeft: isOpen ? '1px solid var(--right-panel-border)' : 'none',
      display: isOpen ? 'flex' : 'none',
      flexDirection: 'column',
      background: 'var(--right-panel-bg)',
      transition: 'width 0.3s ease',
      height: '100vh',
      overflow: 'hidden',
    }}>
      <div className="right-panel-header" style={{
        padding: '10px',
        borderBottom: '1px solid var(--right-panel-border)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '13px',
        fontWeight: '600',
        background: 'var(--right-panel-header-bg)',
        color: 'var(--right-panel-header-text)',
      }}>
        <span>Todo & Process</span>
        <button
          className="right-panel-toggle"
          onClick={onToggle}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontSize: '16px',
            padding: '4px 8px',
            color: 'var(--text-color)',
          }}
        >
          ✕
        </button>
      </div>

      {/* TOP: TODO + PROCESS */}
      <div className="right-panel-top" style={{
        flex: '0 0 45%',
        display: 'flex',
        flexDirection: 'column',
        borderBottom: '1px solid var(--right-panel-border)',
        minHeight: 0,
      }}>
        <div className="right-tab" style={{
          display: 'flex',
          borderBottom: '1px solid var(--right-panel-border)',
        }}>
          <button
            className={`right-tab-btn ${activeTab === 'todo' ? 'active' : ''}`}
            onClick={() => setActiveTab('todo')}
            style={{
              flex: 1,
              padding: '8px',
              border: 'none',
              background: activeTab === 'todo' ? 'var(--right-panel-bg)' : 'rgba(0, 0, 0, 0.03)',
              cursor: 'pointer',
              fontSize: '12px',
              borderBottom: activeTab === 'todo' ? '2px solid #007AFF' : '2px solid transparent',
              color: 'var(--text-color)',
              fontWeight: activeTab === 'todo' ? '600' : '400',
            }}
          >
            Todo
          </button>
          <button
            className={`right-tab-btn ${activeTab === 'process' ? 'active' : ''}`}
            onClick={() => setActiveTab('process')}
            style={{
              flex: 1,
              padding: '8px',
              border: 'none',
              background: activeTab === 'process' ? 'var(--right-panel-bg)' : 'rgba(0, 0, 0, 0.03)',
              cursor: 'pointer',
              fontSize: '12px',
              borderBottom: activeTab === 'process' ? '2px solid #007AFF' : '2px solid transparent',
              color: 'var(--text-color)',
              fontWeight: activeTab === 'process' ? '600' : '400',
            }}
          >
            Process
          </button>
        </div>

        <div className="right-panel-content" style={{
          flex: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          padding: '10px',
          display: 'flex',
          flexDirection: 'column',
          minHeight: 0,
        }}>
          {activeTab === 'todo' && (
            <div className="right-tab-content active">
              {!sessionId ? (
                <p style={{ fontSize: '11px', color: '#999' }}>Aucune conversation sélectionnée</p>
              ) : todos.length === 0 ? (
                <p style={{ fontSize: '11px', color: '#999' }}>Aucune tâche pour le moment</p>
              ) : (
                todos.map((todo, idx) => (
                  <div
                    key={idx}
                    className={`todo-item ${todo.done ? 'done' : ''}`}
                    style={{
                      padding: '8px',
                      border: '1px solid var(--right-panel-border)',
                      borderRadius: '4px',
                      marginBottom: '6px',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '8px',
                      background: 'var(--right-panel-bg)',
                      opacity: todo.done ? 0.6 : 1,
                      textDecoration: todo.done ? 'line-through' : 'none',
                    }}
                  >
                    <input
                      type="checkbox"
                      className="todo-checkbox"
                      checked={todo.done}
                      disabled
                      style={{ marginTop: '2px' }}
                    />
                    <div className="todo-content" style={{
                      flex: 1,
                      fontSize: '12px',
                      lineHeight: '1.4',
                      color: 'var(--text-color)',
                    }}>
                      {todo.text || ''}
                      {todo.timestamp && (
                        <div className="todo-time" style={{
                          fontSize: '10px',
                          color: 'var(--time-color)',
                          marginTop: '4px',
                        }}>
                          {formatTime(todo.timestamp)}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'process' && (
            <div className="right-tab-content active">
              {!sessionId ? (
                <p style={{ fontSize: '11px', color: '#999' }}>Aucune conversation sélectionnée</p>
              ) : logs.length === 0 ? (
                <p style={{ fontSize: '11px', color: '#999' }}>Aucune action pour le moment</p>
              ) : (
                logs.slice(-30).reverse().map((log, idx) => {
                  const text = log.text || ''
                  const isError = !log.success || text.includes('❌') || text.includes('ERREUR') || text.toLowerCase().includes('error')
                  const isSuccess = log.success && (text.includes('✓') || text.includes('Résultat:') || text.includes('success'))
                  const actionType = log.type || 'unknown'
                  
                  return (
                    <div
                      key={idx}
                      className={`process-entry ${isError ? 'error' : isSuccess ? 'success' : ''}`}
                      style={{
                        padding: '8px',
                        borderLeft: `3px solid ${isError ? '#ff3b30' : isSuccess ? '#34c759' : '#007AFF'}`,
                        marginBottom: '8px',
                        background: isError ? 'rgba(255, 59, 48, 0.1)' : isSuccess ? 'rgba(52, 199, 89, 0.1)' : 'rgba(0, 0, 0, 0.02)',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontFamily: 'monospace',
                        color: 'var(--text-color)',
                      }}
                    >
                      {log.timestamp && (
                        <div className="process-time" style={{
                          fontSize: '10px',
                          color: 'var(--time-color)',
                          marginBottom: '4px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                        }}>
                          <span>{formatTime(log.timestamp)}</span>
                          {actionType && (
                            <span style={{
                              fontSize: '9px',
                              opacity: 0.7,
                              textTransform: 'uppercase',
                            }}>
                              {actionType}
                            </span>
                          )}
                        </div>
                      )}
                      <div className="process-text" style={{
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        lineHeight: '1.5',
                      }}>
                        {escapeHtml(text)}
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          )}
        </div>
      </div>

      {/* BOTTOM: THINK */}
      <div className="right-panel-bottom" style={{
        flex: '0 0 55%',
        display: 'flex',
        flexDirection: 'column',
        minHeight: 0,
        border: '2px solid var(--think-border)',
        borderRadius: '6px',
        margin: '4px',
        overflow: 'hidden',
        background: 'var(--think-bg)',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      }}>
        <div className="think-header" style={{
          padding: '8px 10px',
          borderBottom: '2px solid var(--think-border)',
          fontSize: '12px',
          fontWeight: '600',
          background: 'var(--think-header-bg)',
          color: 'var(--think-header-text)',
          flexShrink: 0,
        }}>
          <span><span style={{ filter: 'grayscale(100%)', opacity: 0.6, marginRight: '4px', display: 'inline-block' }}>🧠</span> Think</span>
        </div>
        <div
          ref={thinkContentRef}
          className="think-content"
          style={{
            flex: 1,
            overflowY: 'auto',
            overflowX: 'hidden',
            padding: '10px',
            paddingBottom: '10px',
            minHeight: 0,
            wordWrap: 'break-word',
            overflowWrap: 'break-word',
            boxSizing: 'border-box',
            position: 'relative',
            maxHeight: '100%',
            borderBottom: '2px solid var(--think-border)',
          }}
        >
          {!sessionId ? (
            <p style={{ fontSize: '11px', color: '#999' }}>Aucune conversation sélectionnée</p>
          ) : thinking.length === 0 ? (
            <p style={{ fontSize: '11px', color: '#999' }}>Aucune réflexion pour le moment</p>
          ) : (
            thinking.slice(-20).reverse().map((thought, idx) => {
              const thoughtType = thought.type || 'unknown'
              const isPreFetch = thoughtType === 'pre_fetch'
              const isLLMThought = thoughtType === 'llm_thought' || thoughtType === 'internal_thought'
              const timestamp = thought.timestamp || thought.ts
              
              return (
                <div
                  key={idx}
                  className="think-entry"
                  style={{
                    padding: '8px',
                    marginBottom: '6px',
                    fontSize: '11px',
                    lineHeight: '1.5',
                    color: 'var(--text-color)',
                    borderBottom: idx < thinking.length - 1 ? '1px solid rgba(0, 0, 0, 0.05)' : 'none',
                    background: isPreFetch ? 'rgba(0, 122, 255, 0.05)' : isLLMThought ? 'rgba(255, 193, 7, 0.05)' : 'transparent',
                    borderLeft: isPreFetch ? '3px solid #007AFF' : isLLMThought ? '3px solid #FFC107' : 'none',
                    paddingLeft: isPreFetch || isLLMThought ? '11px' : '8px',
                  }}
                >
                  {timestamp && (
                    <div className="think-time" style={{
                      fontSize: '9px',
                      color: 'var(--time-color)',
                      marginBottom: '4px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}>
                      <span>{formatTime(timestamp)}</span>
                      {thoughtType && (
                        <span style={{
                          fontSize: '9px',
                          opacity: 0.7,
                          textTransform: 'uppercase',
                        }}>
                          {thoughtType === 'pre_fetch' ? '📖 Pré-lecture' : thoughtType === 'llm_thought' ? '💭 LLM' : '💭'}
                        </span>
                      )}
                    </div>
                  )}
                  <div className="think-text" style={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    color: 'var(--think-text)',
                  }}>
                    {escapeHtml(thought.text || '')}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>
    </div>
  )
}

