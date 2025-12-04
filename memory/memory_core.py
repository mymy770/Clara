# Clara - Memory Core
"""
Système de mémoire (placeholder minimal pour Phase 1)
"""

import sqlite3
from pathlib import Path
from datetime import datetime


class MemoryCore:
    """Gestionnaire de mémoire Clara (placeholder minimal)"""
    
    def __init__(self, db_path="memory/clara_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialise la base de données"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Table simple pour les interactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_message TEXT,
                clara_response TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_interaction(self, session_id, user_message, clara_response):
        """Sauvegarde une interaction"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interactions (session_id, timestamp, user_message, clara_response)
            VALUES (?, ?, ?, ?)
        """, (session_id, datetime.now().isoformat(), user_message, clara_response))
        
        conn.commit()
        conn.close()
    
    def load_context(self, session_id, limit=10):
        """Charge le contexte récent d'une session"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_message, clara_response
            FROM interactions
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (session_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        # Retourner dans l'ordre chronologique
        return list(reversed(results))
