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
-- FORMAT POUR type = 'contact'
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
