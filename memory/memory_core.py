"""
Clara V3 - Memory Core
API centrale pour la gestion de la mémoire (SQLite)
"""

import sqlite3
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryCore:
    """
    Gestionnaire central de la mémoire de Clara
    Interface avec la base SQLite
    """
    
    def __init__(self, db_path: str = "memory/clara_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_database()
        logger.info(f"Memory Core initialized with database: {self.db_path}")
    
    def _init_database(self):
        """Initialise la base de données avec le schéma"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        # Charger et exécuter le schéma
        schema_path = self.db_path.parent / "schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema = f.read()
            self.conn.executescript(schema)
            self.conn.commit()
            logger.info("Database schema initialized")
    
    # --- Contacts ---
    
    def add_contact(self, name: str, phone: str = None, email: str = None, 
                   relation: str = None, tags: List[str] = None, notes: str = None) -> int:
        """Ajoute un contact"""
        cursor = self.conn.cursor()
        tags_json = json.dumps(tags) if tags else None
        cursor.execute("""
            INSERT INTO contacts (name, phone, email, relation, tags, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, phone, email, relation, tags_json, notes))
        self.conn.commit()
        logger.info(f"Contact added: {name}")
        return cursor.lastrowid
    
    def get_contact(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un contact par ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE contact_id = ?", (contact_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Cherche des contacts par nom"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE name LIKE ? OR relation LIKE ?
        """, (f"%{query}%", f"%{query}%"))
        return [dict(row) for row in cursor.fetchall()]
    
    # --- Préférences ---
    
    def set_preference(self, key: str, value: str, scope: str = 'global', 
                      agent_name: str = None, description: str = None):
        """Définit une préférence"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO preferences (key, value, scope, agent_name, description, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (key, value, scope, agent_name, description))
        self.conn.commit()
        logger.info(f"Preference set: {key} = {value}")
    
    def get_preference(self, key: str, scope: str = 'global', 
                      agent_name: str = None) -> Optional[str]:
        """Récupère une préférence"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT value FROM preferences 
            WHERE key = ? AND scope = ? AND (agent_name = ? OR agent_name IS NULL)
        """, (key, scope, agent_name))
        row = cursor.fetchone()
        return row['value'] if row else None
    
    # --- Événements mémoire ---
    
    def add_memory_event(self, session_id: str, event_type: str, content: str,
                        context: Dict[str, Any] = None, importance: int = 5) -> int:
        """Enregistre un événement mémoire"""
        cursor = self.conn.cursor()
        context_json = json.dumps(context) if context else None
        cursor.execute("""
            INSERT INTO memory_events (session_id, event_type, content, context, importance)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, event_type, content, context_json, importance))
        self.conn.commit()
        logger.info(f"Memory event added: {event_type}")
        return cursor.lastrowid
    
    def get_session_events(self, session_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les événements d'une session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM memory_events 
            WHERE session_id = ?
            ORDER BY created_at
        """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # --- État des agents ---
    
    def set_agent_state(self, agent_name: str, key: str, value: str):
        """Définit l'état d'un agent"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO agent_state (agent_name, key, value, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (agent_name, key, value))
        self.conn.commit()
        logger.info(f"Agent state set: {agent_name}.{key}")
    
    def get_agent_state(self, agent_name: str, key: str) -> Optional[str]:
        """Récupère l'état d'un agent"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT value FROM agent_state 
            WHERE agent_name = ? AND key = ?
        """, (agent_name, key))
        row = cursor.fetchone()
        return row['value'] if row else None
    
    def close(self):
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

