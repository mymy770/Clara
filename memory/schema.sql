-- Clara - Schéma SQLite Memory Core
-- Phase 2 : Système de mémoire simple et polyvalent

CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour améliorer les performances de recherche
CREATE INDEX IF NOT EXISTS idx_memory_type ON memory(type);
CREATE INDEX IF NOT EXISTS idx_memory_created_at ON memory(created_at DESC);

-- ============================================
-- TABLE PREFERENCES
-- ============================================
CREATE TABLE IF NOT EXISTS preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scope TEXT,
    agent TEXT,
    domain TEXT,
    key TEXT UNIQUE,
    value TEXT,
    source TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les préférences
CREATE INDEX IF NOT EXISTS idx_preferences_key ON preferences(key);
CREATE INDEX IF NOT EXISTS idx_preferences_scope ON preferences(scope);
CREATE INDEX IF NOT EXISTS idx_preferences_agent ON preferences(agent);

-- ============================================
-- TABLE CONTACTS
-- ============================================
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    display_name TEXT,
    aliases TEXT,           -- JSON list
    category TEXT,          -- "family" | "friend" | "client" | "supplier" | "other"
    relationship TEXT,      -- JSON dict {category, role} or string
    phones TEXT,            -- JSON list
    emails TEXT,            -- JSON list
    company TEXT,
    role TEXT,
    notes TEXT,             -- JSON list
    whatsapp_number TEXT,
    tags TEXT,              -- JSON list
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les contacts
CREATE INDEX IF NOT EXISTS idx_contacts_first_name ON contacts(first_name);
CREATE INDEX IF NOT EXISTS idx_contacts_last_name ON contacts(last_name);
CREATE INDEX IF NOT EXISTS idx_contacts_category ON contacts(category);
CREATE INDEX IF NOT EXISTS idx_contacts_created_at ON contacts(created_at DESC);

-- ============================================
-- FORMAT POUR type = 'contact' (OBSOLÈTE - utiliser table contacts)
-- ============================================
-- Pour type = 'contact', content est un objet JSON avec :
-- {
--   "first_name": string,
--   "last_name": string,
--   "display_name": string,
--   "aliases": [string],              // ["ma femme", "mon frère", ...]
--   "category": string,                // "family" | "friend" | "client" | "supplier" | "other"
--   "relationship": string,            // "wife", "brother", "best_friend", ...
--   "phones": [                        // Liste de téléphones
--     {
--       "number": string,              // "+972-5x-xxx-xxxx"
--       "label": string,               // "perso" | "pro" | "other"
--       "primary": boolean,            // true si numéro principal
--       "channels": [string]           // ["call", "sms", "whatsapp", "telegram"]
--     }
--   ],
--   "emails": [                        // Liste d'emails
--     {
--       "address": string,             // "email@example.com"
--       "label": string,               // "perso" | "pro" | "other"
--       "primary": boolean             // true si email principal
--     }
--   ],
--   "company": string | null,          // Entreprise
--   "role": string | null,             // Rôle dans l'entreprise
--   "notes": [string]                  // Notes libres
-- }
