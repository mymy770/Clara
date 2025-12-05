// Clara - API Client

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export async function sendMessage(message, sessionId = null, debug = false) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      debug,
    }),
  })
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }
  
  return await response.json()
}

export async function listSessions() {
  const response = await fetch(`${API_BASE}/sessions`)
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }
  
  return await response.json()
}

export async function loadSession(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}`)
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }
  
  return await response.json()
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`)
  return await response.json()
}

export async function renameSession(sessionId, newTitle) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/rename`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title: newTitle }),
  })
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }
  
  return await response.json()
}

export async function deleteSession(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE',
  })
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }
  
  return await response.json()
}

export async function deleteAllSessions() {
  const response = await fetch(`${API_BASE}/sessions`, {
    method: 'DELETE',
  })
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }
  
  return await response.json()
}

export async function getSessionTodos(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/todos`)
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }
  
  return await response.json()
}

export async function getSessionLogs(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/logs`)
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }
  
  return await response.json()
}

export async function getSessionThinking(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/thinking`)
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }
  
  return await response.json()
}

export async function createSession() {
  const response = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
  })
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`)
  }
  
  return await response.json()
}

