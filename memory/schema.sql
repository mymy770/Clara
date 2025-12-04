-- Clara - Schéma SQLite
-- Base de données structurée pour la mémoire de Clara
-- Date: 2025-12-04

-- Table des utilisateurs (multi-personnes si nécessaire)
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des contacts (personnes importantes)
CREATE TABLE IF NOT EXISTS contacts (
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    relation TEXT,  -- ex: "épouse", "collègue", "ami"
    tags TEXT,      -- JSON array de tags
    notes TEXT,     -- Notes libres
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des préférences (configuration et préférences utilisateur)
CREATE TABLE IF NOT EXISTS preferences (
    pref_id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    scope TEXT DEFAULT 'global',  -- 'global', 'agent', 'context'
    agent_name TEXT,              -- Si scope='agent'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(key, scope, agent_name)
);

-- Table des protocoles (procédures, checklists, workflows)
CREATE TABLE IF NOT EXISTS protocols (
    protocol_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    steps TEXT NOT NULL,  -- JSON array des étapes
    category TEXT,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des événements mémoire (événements marquants)
CREATE TABLE IF NOT EXISTS memory_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    event_type TEXT NOT NULL,  -- 'decision', 'important_fact', 'preference_learned', etc.
    content TEXT NOT NULL,
    context TEXT,              -- JSON context supplémentaire
    importance INTEGER DEFAULT 5,  -- 1-10
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de l'état des agents (état persistant par agent)
CREATE TABLE IF NOT EXISTS agent_state (
    state_id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_name, key)
);

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name);
CREATE INDEX IF NOT EXISTS idx_preferences_key ON preferences(key);
CREATE INDEX IF NOT EXISTS idx_memory_events_session ON memory_events(session_id);
CREATE INDEX IF NOT EXISTS idx_memory_events_type ON memory_events(event_type);
CREATE INDEX IF NOT EXISTS idx_agent_state_agent ON agent_state(agent_name);

