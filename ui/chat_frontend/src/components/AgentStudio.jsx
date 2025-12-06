import React, { useState, useEffect, useRef } from 'react'
import { getAutogenAgents, getAutogenMessages } from '../api'

export default function AgentStudio({ sessionId, isOpen, onToggle }) {
  const [agents, setAgents] = useState([])
  const [messages, setMessages] = useState([])
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [autoScroll, setAutoScroll] = useState(true)
  const [viewMode, setViewMode] = useState('graph') // 'graph' ou 'timeline'
  const messagesEndRef = useRef(null)
  const canvasRef = useRef(null)

  useEffect(() => {
    if (sessionId && isOpen) {
      loadAgents()
      loadMessages()
      const interval = setInterval(() => {
        if (sessionId && isOpen) {
          loadMessages()
        }
      }, 1000) // Rafraîchir toutes les secondes pour le live
      return () => clearInterval(interval)
    } else {
      // Réinitialiser si fermé
      setAgents([])
      setMessages([])
    }
  }, [sessionId, isOpen])

  useEffect(() => {
    if (autoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, autoScroll])

  useEffect(() => {
    if (viewMode === 'graph' && canvasRef.current) {
      drawGraph()
    }
  }, [messages, agents, viewMode])

  async function loadAgents() {
    if (!sessionId) {
      console.warn('AgentStudio: No sessionId provided')
      return
    }
    try {
      const data = await getAutogenAgents(sessionId)
      setAgents(data.agents || [])
    } catch (error) {
      console.error('Error loading agents:', error)
      // Afficher l'erreur à l'utilisateur
      if (error.message.includes('Failed to fetch')) {
        console.error('API non accessible. Vérifiez que le serveur tourne sur http://localhost:8001')
      }
    }
  }

  async function loadMessages() {
    if (!sessionId) {
      console.warn('AgentStudio: No sessionId provided')
      return
    }
    try {
      const data = await getAutogenMessages(sessionId)
      setMessages(data.messages || [])
    } catch (error) {
      console.error('Error loading messages:', error)
      // Ne pas spammer la console si l'API n'est pas accessible
      if (!error.message.includes('Failed to fetch')) {
        console.error('Erreur chargement messages:', error)
      }
    }
  }

  function getAgentColor(agentName) {
    const colors = {
      'interpreter': '#3b82f6',
      'fs_agent': '#10b981',
      'memory_agent': '#f59e0b',
      'user_proxy': '#6b7280',
      'user': '#8b5cf6',
    }
    return colors[agentName] || '#9ca3af'
  }

  function drawGraph() {
    const canvas = canvasRef.current
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight
    
    // Clear
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Nodes: User + Agents
    const nodes = [
      { id: 'user', name: 'Vous', x: 50, y: canvas.height / 2, color: '#8b5cf6' },
    ]
    
    // Ajouter les agents
    const agentSpacing = (canvas.height - 100) / Math.max(agents.length, 1)
    agents.forEach((agent, idx) => {
      nodes.push({
        id: agent.name,
        name: agent.name,
        x: canvas.width - 50,
        y: 50 + idx * agentSpacing,
        color: getAgentColor(agent.name),
      })
    })
    
    // Dessiner les edges (messages) avec animation
    messages.forEach((msg, idx) => {
      const fromNode = msg.name === 'user_proxy' || !msg.name ? nodes[0] : nodes.find(n => n.id === msg.name) || nodes[0]
      const toNode = nodes.find(n => n.id === 'interpreter') || nodes[1] || nodes[0]
      
      if (fromNode && toNode) {
        // Animation: les messages récents sont plus visibles
        const age = messages.length - idx
        const opacity = Math.min(1, age / 10)
        const lineWidth = age <= 3 ? 3 : 1
        
        ctx.strokeStyle = `rgba(${parseInt(fromNode.color.slice(1, 3), 16)}, ${parseInt(fromNode.color.slice(3, 5), 16)}, ${parseInt(fromNode.color.slice(5, 7), 16)}, ${opacity})`
        ctx.lineWidth = lineWidth
        ctx.setLineDash(age <= 3 ? [] : [5, 5])
        
        ctx.beginPath()
        ctx.moveTo(fromNode.x, fromNode.y)
        ctx.lineTo(toNode.x, toNode.y)
        ctx.stroke()
        
        // Flèche animée pour les messages récents
        if (age <= 3) {
          const angle = Math.atan2(toNode.y - fromNode.y, toNode.x - fromNode.x)
          const arrowX = toNode.x - 15 * Math.cos(angle)
          const arrowY = toNode.y - 15 * Math.sin(angle)
          
          ctx.fillStyle = fromNode.color
          ctx.beginPath()
          ctx.moveTo(arrowX, arrowY)
          ctx.lineTo(arrowX - 10 * Math.cos(angle - Math.PI / 6), arrowY - 10 * Math.sin(angle - Math.PI / 6))
          ctx.lineTo(arrowX - 10 * Math.cos(angle + Math.PI / 6), arrowY - 10 * Math.sin(angle + Math.PI / 6))
          ctx.closePath()
          ctx.fill()
        }
      }
    })
    
    // Dessiner les nodes
    nodes.forEach(node => {
      // Cercle
      ctx.fillStyle = node.color
      ctx.beginPath()
      ctx.arc(node.x, node.y, 20, 0, 2 * Math.PI)
      ctx.fill()
      
      // Bordure
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 2
      ctx.stroke()
      
      // Label
      ctx.fillStyle = '#000'
      ctx.font = '12px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText(node.name, node.x, node.y + 35)
    })
  }

  if (!isOpen) return null

  // Afficher un message si pas de sessionId
  if (!sessionId) {
    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'var(--main-bg)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        gap: '20px',
      }}>
        <h2>🤖 Studio Clara</h2>
        <p style={{ color: 'var(--text-color-secondary)' }}>
          Aucune session active. Envoyez un message dans le chat pour commencer.
        </p>
        <button
          onClick={onToggle}
          style={{
            padding: '10px 20px',
            background: 'var(--button-bg)',
            color: 'var(--button-text)',
            border: '1px solid var(--button-border)',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Fermer
        </button>
      </div>
    )
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'var(--main-bg)',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* Header */}
      <div style={{
        padding: '15px 20px',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'var(--header-bg)',
      }}>
        <h2 style={{ margin: 0, fontSize: '18px', fontWeight: '600' }}>
          🤖 Studio Clara - Flux en Temps Réel
        </h2>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <select
            value={viewMode}
            onChange={(e) => setViewMode(e.target.value)}
            style={{
              padding: '6px 10px',
              background: 'var(--input-bg)',
              color: 'var(--input-text)',
              border: '1px solid var(--input-border)',
              borderRadius: '4px',
              fontSize: '12px',
            }}
          >
            <option value="graph">Graphique</option>
            <option value="timeline">Timeline</option>
          </select>
          <label style={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: '5px' }}>
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
            />
            Auto-scroll
          </label>
          <button
            onClick={onToggle}
            style={{
              padding: '6px 12px',
              background: 'var(--button-bg)',
              color: 'var(--button-text)',
              border: '1px solid var(--button-border)',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Fermer
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Sidebar - Liste des agents */}
        <div style={{
          width: '250px',
          borderRight: '1px solid var(--border-color)',
          overflowY: 'auto',
          background: 'var(--sidebar-bg)',
        }}>
          <div style={{ padding: '15px' }}>
            <h3 style={{ margin: '0 0 10px 0', fontSize: '14px', fontWeight: '600' }}>
              Agents ({agents.length})
            </h3>
            {agents.map((agent) => {
              const messageCount = messages.filter(m => m.name === agent.name).length
              return (
                <div
                  key={agent.name}
                  onClick={() => setSelectedAgent(selectedAgent === agent.name ? null : agent.name)}
                  style={{
                    padding: '10px',
                    marginBottom: '8px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    background: selectedAgent === agent.name ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                    border: `1px solid ${selectedAgent === agent.name ? getAgentColor(agent.name) : 'transparent'}`,
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: '5px',
                  }}>
                    <div style={{
                      width: '10px',
                      height: '10px',
                      borderRadius: '50%',
                      background: getAgentColor(agent.name),
                    }} />
                    <span style={{ fontWeight: '600', fontSize: '13px' }}>
                      {agent.name}
                    </span>
                    <span style={{
                      fontSize: '10px',
                      padding: '2px 6px',
                      background: 'rgba(0,0,0,0.1)',
                      borderRadius: '3px',
                    }}>
                      {messageCount}
                    </span>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-color-secondary)', marginTop: '5px' }}>
                    {agent.functions.length} fonction(s)
                  </div>
                  {agent.functions.length > 0 && (
                    <div style={{ fontSize: '10px', marginTop: '5px', color: 'var(--text-color-secondary)' }}>
                      {agent.functions.slice(0, 3).join(', ')}
                      {agent.functions.length > 3 && '...'}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Main - Graphique ou Timeline */}
        {viewMode === 'graph' ? (
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            position: 'relative',
          }}>
            <div style={{
              padding: '10px 15px',
              borderBottom: '1px solid var(--border-color)',
              fontSize: '12px',
              color: 'var(--text-color-secondary)',
            }}>
              {messages.length} message(s) • {new Set(messages.map(m => m.name)).size} agent(s) actif(s) • 
              <span style={{ color: '#10b981', marginLeft: '5px' }}>●</span> Live
            </div>
            <canvas
              ref={canvasRef}
              style={{
                flex: 1,
                width: '100%',
                height: '100%',
                background: 'var(--main-bg)',
              }}
            />
          </div>
        ) : (
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}>
            <div style={{
              padding: '10px 15px',
              borderBottom: '1px solid var(--border-color)',
              fontSize: '12px',
              color: 'var(--text-color-secondary)',
            }}>
              {messages.length} message(s) • {new Set(messages.map(m => m.name)).size} agent(s) actif(s)
            </div>

            <div style={{
              flex: 1,
              overflowY: 'auto',
              padding: '15px',
            }}>
              {messages.map((msg, idx) => {
                const agentColor = getAgentColor(msg.name)
                const hasFunctionCall = msg.function_call && msg.function_call.name
                const isRecent = messages.length - idx <= 3
                
                return (
                  <div
                    key={idx}
                    style={{
                      marginBottom: '15px',
                      padding: '12px',
                      borderRadius: '8px',
                      background: selectedAgent && msg.name === selectedAgent
                        ? 'rgba(59, 130, 246, 0.05)'
                        : isRecent
                        ? 'rgba(16, 185, 129, 0.05)'
                        : 'var(--input-bg)',
                      borderLeft: `3px solid ${agentColor}`,
                      animation: isRecent ? 'pulse 2s infinite' : 'none',
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '8px',
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: agentColor,
                        }} />
                        <span style={{ fontWeight: '600', fontSize: '13px' }}>
                          {msg.name || 'unknown'}
                        </span>
                        {hasFunctionCall && (
                          <span style={{
                            fontSize: '10px',
                            padding: '2px 6px',
                            background: '#f59e0b',
                            color: 'white',
                            borderRadius: '3px',
                          }}>
                            🔧 {msg.function_call.name}
                          </span>
                        )}
                        {isRecent && (
                          <span style={{
                            fontSize: '10px',
                            padding: '2px 6px',
                            background: '#10b981',
                            color: 'white',
                            borderRadius: '3px',
                          }}>
                            LIVE
                          </span>
                        )}
                      </div>
                      <span style={{ fontSize: '11px', color: 'var(--text-color-secondary)' }}>
                        #{idx + 1}
                      </span>
                    </div>

                    {hasFunctionCall && (
                      <div style={{
                        marginBottom: '8px',
                        padding: '8px',
                        background: 'rgba(245, 158, 11, 0.1)',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontFamily: 'monospace',
                      }}>
                        <div style={{ fontWeight: '600', marginBottom: '4px' }}>
                          Function Call: {msg.function_call.name}
                        </div>
                        {msg.function_call.arguments && (
                          <pre style={{ margin: 0, fontSize: '10px', whiteSpace: 'pre-wrap' }}>
                            {typeof msg.function_call.arguments === 'string'
                              ? msg.function_call.arguments
                              : JSON.stringify(msg.function_call.arguments, null, 2)}
                          </pre>
                        )}
                      </div>
                    )}

                    {msg.content && (
                      <div style={{
                        fontSize: '12px',
                        lineHeight: '1.5',
                        whiteSpace: 'pre-wrap',
                        color: 'var(--text-color)',
                      }}>
                        {msg.content}
                      </div>
                    )}
                  </div>
                )
              })}
              <div ref={messagesEndRef} />
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      `}</style>
    </div>
  )
}

