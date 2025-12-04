# Clara - Logger
"""
Système de logs pour Clara
- logs/sessions/<id>.txt : transcript humain
- logs/debug/<id>.json : debug complet
"""

import json
from pathlib import Path
from datetime import datetime


class SessionLogger:
    """Logger pour les transcripts de session (format humain)"""
    
    def __init__(self, session_id, logs_dir="logs/sessions"):
        self.session_id = session_id
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.logs_dir / f"{session_id}.txt"
        
        # Écrire l'en-tête
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Clara Session {session_id} ===\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
    
    def log_user(self, message):
        """Log un message utilisateur"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Utilisateur:\n{message}\n\n")
    
    def log_clara(self, message):
        """Log une réponse de Clara"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Clara:\n{message}\n\n")


class DebugLogger:
    """Logger pour le debug complet (format JSON)"""
    
    def __init__(self, session_id, logs_dir="logs/debug"):
        self.session_id = session_id
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.logs_dir / f"{session_id}.json"
        self.entries = []
    
    def log_interaction(self, user_input, prompt_messages, llm_response, usage, error=None):
        """Log une interaction complète"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'prompt_messages': prompt_messages,
            'llm_response': llm_response,
            'usage': usage,
            'error': error
        }
        self.entries.append(entry)
        self._write()
    
    def _write(self):
        """Écrit les logs dans le fichier JSON"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump({
                'session_id': self.session_id,
                'interactions': self.entries
            }, f, indent=2, ensure_ascii=False)

