#!/usr/bin/env python3
# Clara - API HTTP Server
"""
Serveur API HTTP pour Clara
Expose Clara via FastAPI pour l'UI de chat
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configurer le logging
log_level = os.getenv('CLARA_LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.orchestrator import Orchestrator
from utils.logger import SessionLogger, DebugLogger
from memory.memory_core import init_db

# Initialiser la base de données au démarrage
init_db()

# Créer l'app FastAPI
app = FastAPI(title="Clara API", version="1.0.0")

# CORS pour permettre l'UI de se connecter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En dev, on autorise tout. En prod, spécifier les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Orchestrateur global (réutilisé pour toutes les requêtes)
orchestrator = Orchestrator()


def generate_session_id():
    """Génère un ID de session unique"""
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


# ============================================
# Modèles Pydantic
# ============================================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    debug: bool = False


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    debug: Optional[dict] = None


class SessionInfo(BaseModel):
    session_id: str
    started_at: str
    title: Optional[str] = None


# ============================================
# Endpoints
# ============================================

@app.get("/health")
async def health():
    """Endpoint de santé"""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal pour envoyer un message à Clara
    
    - Si session_id absent → crée une nouvelle session
    - Appelle l'orchestrateur comme run_clara.py
    - Retourne la réponse avec debug optionnel
    """
    try:
        # Gérer la session
        session_id = request.session_id
        if not session_id:
            session_id = generate_session_id()
        
        # Initialiser les loggers pour cette session
        session_logger = SessionLogger(session_id)
        debug_logger = DebugLogger(session_id)
        
        # Logger l'input utilisateur
        session_logger.log_user(request.message)
        
        # Appeler l'orchestrateur (même logique que run_clara.py)
        response = orchestrator.handle_message(request.message, session_id, debug_logger)
        
        # Logger la réponse
        session_logger.log_clara(response)
        
        # Préparer la réponse
        result = ChatResponse(
            reply=response,
            session_id=session_id
        )
        
        # Ajouter debug si demandé
        if request.debug:
            # Pour l'instant, on peut extraire des infos basiques
            # Plus tard, on pourra enrichir avec intents, actions mémoire, etc.
            result.debug = {
                "session_id": session_id,
                "message_length": len(request.message),
                "response_length": len(response)
            }
        
        return result
        
    except Exception as e:
        logging.exception(f"Erreur dans /chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions", response_model=list[SessionInfo])
async def list_sessions():
    """
    Liste toutes les sessions existantes
    Basé sur les fichiers dans logs/sessions/
    """
    sessions = []
    sessions_dir = Path("logs/sessions")
    
    if not sessions_dir.exists():
        return sessions
    
    # Parcourir les fichiers de session
    for session_file in sessions_dir.glob("session_*.txt"):
        session_id = session_file.stem
        
        # Extraire la date de création du fichier
        try:
            stat = session_file.stat()
            started_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except Exception:
            started_at = datetime.now().isoformat()
        
        # Essayer d'extraire un titre depuis le premier message (optionnel)
        title = None
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Chercher le premier message utilisateur
                for i, line in enumerate(lines):
                    if "Utilisateur:" in line and i + 1 < len(lines):
                        first_msg = lines[i + 1].strip()
                        if first_msg:
                            title = first_msg[:50]  # Limiter à 50 caractères
                            break
        except Exception:
            pass
        
        sessions.append(SessionInfo(
            session_id=session_id,
            started_at=started_at,
            title=title
        ))
    
    # Trier par date (plus récent en premier)
    sessions.sort(key=lambda x: x.started_at, reverse=True)
    
    return sessions


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Récupère l'historique d'une session
    Parse le fichier de session et retourne les messages
    """
    session_file = Path(f"logs/sessions/{session_id}.txt")
    
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = []
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Parser le format de session
            # Format: [HH:MM:SS] Role:\nmessage\n
            import re
            pattern = r'\[(\d{2}:\d{2}:\d{2})\]\s*(Utilisateur|Clara):\n(.*?)(?=\n\[|\Z)'
            matches = re.findall(pattern, content, re.DOTALL)
            
            for timestamp, role, message in matches:
                role_clean = "user" if role == "Utilisateur" else "assistant"
                messages.append({
                    "role": role_clean,
                    "content": message.strip(),
                    "timestamp": timestamp
                })
    
    except Exception as e:
        logging.exception(f"Erreur parsing session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing session: {str(e)}")
    
    return {
        "session_id": session_id,
        "messages": messages
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)

