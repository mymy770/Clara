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
from drivers.fs_driver import FSDriver
from agents.helpers import set_fs_driver
import json
import warnings
# Supprimer les warnings Pydantic d'Autogen
warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')

# Import Autogen (optionnel, ne plante pas si non installé)
try:
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    from agents.autogen_hub import (
        build_llm_config,
        create_fs_agent,
        create_memory_agent,
        create_interpreter_agent,
    )
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    logging.warning("Autogen non disponible. Le mode Autogen sera désactivé.")

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

# Initialiser le driver filesystem
workspace_root = Path(__file__).resolve().parent
fs_driver = FSDriver(root_path=workspace_root)
set_fs_driver(fs_driver)

# Orchestrateur global (réutilisé pour toutes les requêtes)
orchestrator = Orchestrator(fs_driver=fs_driver)

# Instances Autogen globales (créées à la première utilisation)
autogen_instances = {
    'llm_config': None,
    'fs_agent': None,
    'memory_agent': None,
    'interpreter': None,
    'groupchat': None,
    'manager': None,
    'user_proxy': None,
}

def init_autogen_instances():
    """Initialise les instances Autogen une seule fois"""
    if not AUTOGEN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Autogen non disponible")
    
    if autogen_instances['manager'] is None:
        logging.info("Initialisation des agents Autogen...")
        workspace_root = Path(__file__).resolve().parent
        
        llm_config = build_llm_config()
        fs_agent = create_fs_agent(llm_config, workspace_root)
        memory_agent = create_memory_agent(llm_config)
        interpreter = create_interpreter_agent(llm_config, fs_agent, memory_agent)
        
        groupchat = GroupChat(
            agents=[interpreter, fs_agent, memory_agent],
            messages=[],
            max_round=3,
        )
        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config=llm_config,
        )
        user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config=False,
        )
        
        autogen_instances['llm_config'] = llm_config
        autogen_instances['fs_agent'] = fs_agent
        autogen_instances['memory_agent'] = memory_agent
        autogen_instances['interpreter'] = interpreter
        autogen_instances['groupchat'] = groupchat
        autogen_instances['manager'] = manager
        autogen_instances['user_proxy'] = user_proxy
        logging.info("✓ Agents Autogen initialisés")
    
    return autogen_instances


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
    internal: Optional[dict] = None


class SessionInfo(BaseModel):
    session_id: str
    started_at: str
    title: Optional[str] = None


class RenamePayload(BaseModel):
    title: str


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
        orchestrator_response = orchestrator.handle_message(request.message, session_id, debug_logger)
        
        # L'orchestrator retourne maintenant un dict avec 'response' et 'internal'
        if isinstance(orchestrator_response, dict):
            clara_response_text = orchestrator_response.get('response', '')
            internal_data = orchestrator_response.get('internal', {})
        else:
            # Compatibilité avec l'ancien format (string)
            clara_response_text = orchestrator_response
            internal_data = {}
        
        # Logger la réponse
        session_logger.log_clara(clara_response_text)
        
        # Préparer la réponse
        result = ChatResponse(
            reply=clara_response_text,
            session_id=session_id
        )
        
        # Ajouter les données internes
        result.internal = internal_data
        
        # Ajouter debug si demandé
        if request.debug:
            result.debug = {
                "session_id": session_id,
                "message_length": len(request.message),
                "response_length": len(clara_response_text),
                "internal": internal_data
            }
        
        return result
        
    except Exception as e:
        logging.exception(f"Erreur dans /chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def load_session_titles():
    """Charge les titres des sessions depuis un fichier JSON"""
    titles_file = Path("logs/sessions/_titles.json")
    if titles_file.exists():
        try:
            with open(titles_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_session_titles(titles):
    """Sauvegarde les titres des sessions dans un fichier JSON"""
    titles_file = Path("logs/sessions/_titles.json")
    titles_file.parent.mkdir(parents=True, exist_ok=True)
    with open(titles_file, 'w', encoding='utf-8') as f:
        json.dump(titles, f, indent=2, ensure_ascii=False)


@app.get("/sessions", response_model=list[SessionInfo])
async def list_sessions():
    """
    Liste toutes les sessions existantes
    Basé sur les fichiers dans logs/sessions/
    """
    sessions = []
    sessions_dir = Path("logs/sessions")
    titles = load_session_titles()
    
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
        
        # Titre depuis le fichier de métadonnées ou depuis le premier message
        title = titles.get(session_id)
        if not title:
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


@app.post("/sessions/{session_id}/rename")
async def rename_session(session_id: str, payload: RenamePayload):
    """
    Renomme une session
    """
    session_file = Path(f"logs/sessions/{session_id}.txt")
    
    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Charger et mettre à jour les titres
    titles = load_session_titles()
    titles[session_id] = payload.title
    save_session_titles(titles)
    
    return {"success": True, "session_id": session_id, "title": payload.title}


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Supprime une session
    """
    session_file = Path(f"logs/sessions/{session_id}.txt")
    debug_file = Path(f"logs/debug/{session_id}.json")
    titles = load_session_titles()
    
    deleted = False
    
    if session_file.exists():
        session_file.unlink()
        deleted = True
    
    if debug_file.exists():
        debug_file.unlink()
    
    # Supprimer le titre de la liste
    if session_id in titles:
        del titles[session_id]
        save_session_titles(titles)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"success": True, "session_id": session_id}


@app.delete("/sessions")
async def delete_all_sessions():
    """
    Supprime toutes les sessions
    """
    sessions_dir = Path("logs/sessions")
    debug_dir = Path("logs/debug")
    
    deleted_count = 0
    
    if sessions_dir.exists():
        for session_file in sessions_dir.glob("session_*.txt"):
            session_file.unlink()
            deleted_count += 1
    
    if debug_dir.exists():
        for debug_file in debug_dir.glob("session_*.json"):
            debug_file.unlink()
    
    # Supprimer le fichier de titres
    titles_file = Path("logs/sessions/_titles.json")
    if titles_file.exists():
        titles_file.unlink()
    
    return {"success": True, "deleted_count": deleted_count}


@app.post("/sessions")
async def create_session():
    """
    Crée une nouvelle session
    """
    session_id = generate_session_id()
    session_file = Path(f"logs/sessions/{session_id}.txt")
    session_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Créer un fichier vide
    with open(session_file, 'w', encoding='utf-8') as f:
        f.write(f"Session créée le {datetime.now().isoformat()}\n")
    
    return {
        "session_id": session_id,
        "title": None,
        "started_at": datetime.now().isoformat()
    }


@app.get("/sessions/{session_id}/todos")
async def get_session_todos(session_id: str):
    """
    Récupère les todos d'une session depuis la mémoire ou les logs
    """
    # D'abord, essayer de récupérer depuis la mémoire
    try:
        from memory.memory_core import get_items
        todos = get_items(type='todo', limit=50)
        if todos:
            formatted_todos = []
            for todo in todos:
                formatted_todos.append({
                    "text": todo.get('content', ''),
                    "timestamp": todo.get('created_at', ''),
                    "done": False  # Pour l'instant, pas de champ done dans la DB
                })
            return {"todos": formatted_todos}
    except Exception as e:
        logging.exception(f"Erreur récupération todos depuis mémoire: {e}")
    
    # Fallback: extraire depuis les logs
    debug_file = Path(f"logs/debug/{session_id}.json")
    if debug_file.exists():
        try:
            with open(debug_file, 'r', encoding='utf-8') as f:
                debug_data = json.load(f)
            
            todos = []
            if isinstance(debug_data, dict) and "interactions" in debug_data:
                for interaction in debug_data["interactions"]:
                    llm_response = interaction.get('llm_response', '')
                    # Chercher des todos dans la réponse
                    if 'todo' in llm_response.lower() or 'tâche' in llm_response.lower():
                        # Extraire les lignes qui ressemblent à des todos
                        lines = llm_response.split('\n')
                        for line in lines:
                            if any(keyword in line.lower() for keyword in ['-', '•', 'todo', 'tâche', 'faire']):
                                todos.append({
                                    "text": line.strip(),
                                    "timestamp": interaction.get('timestamp', ''),
                                    "done": 'fait' in line.lower() or 'done' in line.lower()
                                })
            
            return {"todos": todos[:20]}  # Limiter à 20
        except Exception as e:
            logging.exception(f"Erreur extraction todos depuis logs: {e}")
    
    return {"todos": []}


@app.get("/sessions/{session_id}/logs")
async def get_session_logs(session_id: str):
    """
    Récupère les commandes de code (process) d'une session depuis le fichier de debug
    Affiche les lignes de code pures qu'elle va exécuter avec tous les détails
    """
    debug_file = Path(f"logs/debug/{session_id}.json")
    
    if not debug_file.exists():
        return {"logs": []}
    
    try:
        with open(debug_file, 'r', encoding='utf-8') as f:
            debug_data = json.load(f)
        
        logs = []
        
        # D'abord, utiliser execution_log si disponible (log détaillé)
        if isinstance(debug_data, dict) and "full_execution_log" in debug_data:
            for exec_entry in debug_data["full_execution_log"]:
                step_type = exec_entry.get('type', 'unknown')
                action = exec_entry.get('action', 'unknown')
                params = exec_entry.get('params', {})
                result = exec_entry.get('result')
                error = exec_entry.get('error')
                
                # Formater selon le type
                if step_type == 'fs_action':
                    # Formater les paramètres
                    params_str = ", ".join([f"{k}={repr(v)[:50]}" for k, v in params.items()])
                    code = f"execute_fs_action('{action}', {{{params_str}}})"
                    
                    if error:
                        code += f"\n  ❌ ERREUR: {error}"
                    elif result and result.get('ok'):
                        code += f"\n  ✓ Résultat: {result.get('message', 'OK')}"
                    else:
                        code += f"\n  ⚠ Résultat: {result}"
                        
                elif step_type == 'memory_action':
                    code = f"{action}({params})"
                    if error:
                        code += f"\n  ❌ ERREUR: {error}"
                    elif result:
                        code += f"\n  ✓ Résultat: {result}"
                        
                elif step_type == 'llm_call':
                    code = f"llm.generate(model='{params.get('model', 'unknown')}', messages={params.get('messages_count', 0)})"
                    if result:
                        code += f"\n  ✓ Tokens: {result.get('usage', {}).get('total_tokens', 'N/A') if isinstance(result.get('usage'), dict) else 'N/A'}"
                
                logs.append({
                    "timestamp": exec_entry.get('timestamp'),
                    "text": code,
                    "type": step_type,
                    "action": action,
                    "success": error is None
                })
        
        # Sinon, fallback sur memory_ops (ancien format)
        elif isinstance(debug_data, dict) and "interactions" in debug_data:
            for interaction in debug_data["interactions"]:
                memory_ops = interaction.get("memory_ops", [])
                for op in memory_ops:
                    action = op.get('action', 'unknown')
                    params = op.get('params', {})
                    
                    # Formater selon le type d'action
                    if action.startswith('FS '):
                        fs_action = action.replace('FS ', '')
                        params_str = ", ".join([f"{k}={repr(v)[:50]}" for k, v in params.items()])
                        code = f"execute_fs_action('{fs_action}', {{{params_str}}})"
                        if op.get('result') == 'error':
                            code += f"\n  ❌ ERREUR: {op.get('error', 'Erreur inconnue')}"
                        else:
                            code += f"\n  ✓ {op.get('result', 'success')}"
                    else:
                        # Actions mémoire
                        code = f"{action}({params})"
                    
                    logs.append({
                        "timestamp": interaction.get("timestamp"),
                        "text": code,
                        "type": "memory_action" if not action.startswith('FS ') else "fs_action",
                        "action": action,
                        "success": op.get('result') != 'error'
                    })
        
        return {"logs": logs[-50:]}  # Dernières 50 exécutions
    except Exception as e:
        logging.exception(f"Erreur lecture logs {session_id}: {e}")
        return {"logs": []}


@app.get("/sessions/{session_id}/thinking")
async def get_session_thinking(session_id: str):
    """
    Récupère les pensées (thinking) d'une session depuis le fichier de debug
    Affiche les vraies réflexions du LLM et les pré-fetches
    """
    debug_file = Path(f"logs/debug/{session_id}.json")
    
    if not debug_file.exists():
        return {"thinking": []}
    
    try:
        with open(debug_file, 'r', encoding='utf-8') as f:
            debug_data = json.load(f)
        
        thinking = []
        
        # D'abord, utiliser execution_log pour les pré-fetches (vraies données lues)
        if isinstance(debug_data, dict) and "full_execution_log" in debug_data:
            for exec_entry in debug_data["full_execution_log"]:
                step_type = exec_entry.get('type', 'unknown')
                
                if step_type == 'fs_pre_fetch':
                    action = exec_entry.get('action', 'unknown')
                    params = exec_entry.get('params', {})
                    result = exec_entry.get('result')
                    error = exec_entry.get('error')
                    
                    if error:
                        text = f"⚠ Pré-lecture {action}({params.get('path', 'N/A')}) : ERREUR - {error}"
                    elif result and result.get('ok'):
                        content = result.get('content', '')
                        text = f"📖 Pré-lecture {action}({params.get('path', 'N/A')}) :\n{content[:500]}"
                    else:
                        text = f"📖 Pré-lecture {action}({params.get('path', 'N/A')}) : Aucun résultat"
                    
                    thinking.append({
                        "timestamp": exec_entry.get('timestamp'),
                        "text": text,
                        "type": "pre_fetch"
                    })
        
        # Ensuite, ajouter les thoughts du LLM depuis internal_data
        if isinstance(debug_data, dict) and "interactions" in debug_data:
            for interaction in debug_data["interactions"]:
                # Extraire la réflexion brute du LLM (premières lignes avant JSON)
                llm_response = interaction.get("llm_response", "")
                if llm_response:
                    # Prendre les premières lignes avant tout JSON
                    lines = llm_response.split('\n')
                    thought_lines = []
                    for line in lines:
                        if '```json' in line or (line.strip().startswith('{') and '"intent"' in line):
                            break
                        thought_lines.append(line)
                    
                    if thought_lines:
                        thoughts_text = '\n'.join(thought_lines).strip()
                        if thoughts_text:
                            thinking.append({
                                "timestamp": interaction.get("timestamp"),
                                "text": f"💭 Réflexion LLM :\n{thoughts_text}",
                                "type": "llm_thought"
                            })
                
                # Ajouter aussi internal_data.thoughts si disponible
                internal_data = interaction.get("internal_data", {})
                thoughts = internal_data.get("thoughts")
                if thoughts and isinstance(thoughts, str) and thoughts.strip():
                    thinking.append({
                        "timestamp": interaction.get("timestamp"),
                        "text": f"💭 {thoughts}",
                        "type": "internal_thought"
                    })
        
        # Format alternatif (si thinking existe directement)
        if isinstance(debug_data, dict):
            if "thinking" in debug_data:
                thinking.extend(debug_data["thinking"])
            elif "thoughts" in debug_data:
                thinking.extend(debug_data["thoughts"])
        
        # Trier par timestamp
        thinking.sort(key=lambda x: x.get('timestamp', x.get('ts', '')))
        
        return {"thinking": thinking[-30:]}  # Dernières 30 réflexions
    except Exception as e:
        logging.exception(f"Erreur lecture thinking {session_id}: {e}")
        return {"thinking": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)

