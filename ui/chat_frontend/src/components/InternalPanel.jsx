import React from 'react'

export default function InternalPanel({
  thoughts,
  todo,
  steps,
  open,
  onToggle,
}) {
  if (!open) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'flex-end',
        padding: '4px',
        borderLeft: '1px solid var(--right-panel-border)',
        background: 'var(--right-panel-bg)',
      }}>
        <button
          onClick={onToggle}
          style={{
            border: 'none',
            background: 'none',
            cursor: 'pointer',
            fontSize: '11px',
            color: 'var(--text-color)',
            padding: '4px 8px',
          }}
        >
          ▶ Détails internes
        </button>
      </div>
    )
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      width: '280px',
      borderLeft: '1px solid var(--right-panel-border)',
      padding: '8px',
      background: 'var(--right-panel-bg)',
      fontSize: '12px',
      color: 'var(--text-color)',
      height: '100vh',
      overflowY: 'auto',
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px',
        fontWeight: '600',
        paddingBottom: '8px',
        borderBottom: '1px solid var(--right-panel-border)',
      }}>
        <span>Détails internes</span>
        <button
          onClick={onToggle}
          style={{
            border: 'none',
            background: 'none',
            cursor: 'pointer',
            fontSize: '16px',
            color: 'var(--text-color)',
            padding: '4px 8px',
          }}
        >
          ✕
        </button>
      </div>

      <div style={{
        marginBottom: '16px',
      }}>
        <h4 style={{
          fontSize: '12px',
          fontWeight: '600',
          marginBottom: '6px',
          color: 'var(--text-color)',
        }}>
          🧠 Réflexion
        </h4>
        {renderThoughts(thoughts)}
      </div>

      <div style={{
        marginBottom: '16px',
      }}>
        <h4 style={{
          fontSize: '12px',
          fontWeight: '600',
          marginBottom: '6px',
          color: 'var(--text-color)',
        }}>
          ✅ Plan d'action
        </h4>
        {renderTodo(todo)}
      </div>

      <div style={{
        marginBottom: '16px',
      }}>
        <h4 style={{
          fontSize: '12px',
          fontWeight: '600',
          marginBottom: '6px',
          color: 'var(--text-color)',
        }}>
          ⚙️ Étapes exécutées
        </h4>
        {renderSteps(steps)}
      </div>
    </div>
  )
}

function renderThoughts(thoughts) {
  if (!thoughts) {
    return (
      <p style={{
        color: '#999',
        fontStyle: 'italic',
        fontSize: '11px',
        margin: 0,
      }}>
        Aucune réflexion disponible.
      </p>
    )
  }

  if (typeof thoughts === 'string') {
    const trimmed = thoughts.split('\n').slice(0, 4).join('\n')
    return (
      <pre style={{
        background: 'var(--sidebar-bg)',
        borderRadius: '4px',
        padding: '6px',
        whiteSpace: 'pre-wrap',
        fontSize: '11px',
        margin: 0,
        overflow: 'hidden',
        maxHeight: '100px',
      }}>
        {trimmed}
      </pre>
    )
  }

  if (Array.isArray(thoughts)) {
    return (
      <ul style={{
        margin: '4px 0',
        paddingLeft: '16px',
        fontSize: '11px',
      }}>
        {thoughts.slice(0, 4).map((t, i) => (
          <li key={i} style={{ marginBottom: '4px' }}>{t}</li>
        ))}
      </ul>
    )
  }

  return (
    <pre style={{
      background: 'var(--sidebar-bg)',
      borderRadius: '4px',
      padding: '6px',
      whiteSpace: 'pre-wrap',
      fontSize: '11px',
      margin: 0,
    }}>
      {JSON.stringify(thoughts, null, 2)}
    </pre>
  )
}

function renderTodo(todo) {
  if (!todo) {
    return (
      <p style={{
        color: '#999',
        fontStyle: 'italic',
        fontSize: '11px',
        margin: 0,
      }}>
        Aucun plan d'action pour le moment.
      </p>
    )
  }

  if (typeof todo === 'string') {
    return (
      <pre style={{
        background: 'var(--sidebar-bg)',
        borderRadius: '4px',
        padding: '6px',
        whiteSpace: 'pre-wrap',
        fontSize: '11px',
        margin: 0,
        overflow: 'hidden',
        maxHeight: '150px',
      }}>
        {todo.split('\n').slice(0, 10).join('\n')}
      </pre>
    )
  }

  if (Array.isArray(todo)) {
    return (
      <ol style={{
        margin: '4px 0',
        paddingLeft: '16px',
        fontSize: '11px',
      }}>
        {todo.slice(0, 10).map((step, i) => (
          <li key={i} style={{ marginBottom: '4px' }}>{step}</li>
        ))}
      </ol>
    )
  }

  return (
    <pre style={{
      background: 'var(--sidebar-bg)',
      borderRadius: '4px',
      padding: '6px',
      whiteSpace: 'pre-wrap',
      fontSize: '11px',
      margin: 0,
    }}>
      {JSON.stringify(todo, null, 2)}
    </pre>
  )
}

function renderSteps(steps) {
  if (!steps) {
    return (
      <p style={{
        color: '#999',
        fontStyle: 'italic',
        fontSize: '11px',
        margin: 0,
      }}>
        Aucune étape exécutée pour le moment.
      </p>
    )
  }

  if (typeof steps === 'string') {
    return (
      <pre style={{
        background: 'var(--sidebar-bg)',
        borderRadius: '4px',
        padding: '6px',
        whiteSpace: 'pre-wrap',
        fontSize: '11px',
        margin: 0,
        overflow: 'hidden',
        maxHeight: '150px',
      }}>
        {steps.split('\n').slice(0, 10).join('\n')}
      </pre>
    )
  }

  if (Array.isArray(steps)) {
    return (
      <ul style={{
        margin: '4px 0',
        paddingLeft: '16px',
        fontSize: '11px',
      }}>
        {steps.slice(0, 10).map((s, i) => (
          <li key={i} style={{ marginBottom: '4px' }}>{s}</li>
        ))}
      </ul>
    )
  }

  return (
    <pre style={{
      background: 'var(--sidebar-bg)',
      borderRadius: '4px',
      padding: '6px',
      whiteSpace: 'pre-wrap',
      fontSize: '11px',
      margin: 0,
    }}>
      {JSON.stringify(steps, null, 2)}
    </pre>
  )
}

