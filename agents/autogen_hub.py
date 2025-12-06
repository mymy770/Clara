# Clara - Autogen Hub
"""
Hub Autogen pour Clara.
Définit les agents :
- InterpreterAgent : agent LLM principal qui parle à l'utilisateur et décide quoi faire
- FSAgent : agent spécialisé dans le filesystem, wrappe fs_driver
- MemoryAgent : agent spécialisé mémoire, wrappe memory_core
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent
except ImportError:
    raise ImportError("pyautogen n'est pas installé. Installez-le avec: pip install pyautogen")

from drivers.fs_driver import FSDriver
from memory.memory_core import init_db, save_item, get_items, search_items, update_item, delete_item
from memory.helpers import save_note, save_todo, save_process, save_protocol
from memory.contacts import save_contact, find_contacts, get_all_contacts, update_contact
from memory.memory_core import save_preference, get_preference_by_key, list_preferences

load_dotenv()


def build_llm_config() -> Dict[str, Any]:
    """Retourne un dict de config pour Autogen (model, api_key, base_url, etc.)"""
    # Réutiliser la config de llm_driver / settings.yaml
    config_path = Path("config/settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in environment variables")
    
    model = cfg.get("model", "gpt-5.1")
    temperature = float(cfg.get("temperature", 0.7))
    base_url = cfg.get("base_url") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    return {
        "temperature": temperature,
        "config_list": [
            {
                "model": model,
                "api_key": api_key,
                "base_url": base_url,
                "price": [0.000002, 0.000006],  # Pour supprimer le warning Autogen
            }
        ],
    }


def create_fs_agent(llm_config: Dict[str, Any], workspace_root: Optional[Path] = None) -> AssistantAgent:
    """Agent spécialisé filesystem. N'a pas de conversation directe avec l'humain."""
    if workspace_root is None:
        workspace_root = Path(__file__).resolve().parent.parent
    
    fs_driver = FSDriver(root_path=workspace_root)
    
    # Fonctions wrapper autour de FSDriver
    def create_dir(path: str) -> str:
        """Crée un dossier. Retourne un message de succès ou d'erreur."""
        try:
            fs_driver.make_dir(path, exist_ok=True)
            return f"✓ Dossier créé : {path}"
        except Exception as e:
            return f"⚠ Erreur création dossier {path} : {str(e)}"
    
    def create_file(path: str, content: str) -> str:
        """Crée un fichier avec le contenu donné. Retourne un message de succès ou d'erreur."""
        try:
            fs_driver.write_text(path, content, overwrite=True)
            return f"✓ Fichier créé : {path} ({len(content)} caractères)"
        except Exception as e:
            return f"⚠ Erreur création fichier {path} : {str(e)}"
    
    def append_to_file(path: str, content: str) -> str:
        """Ajoute du contenu à la fin d'un fichier. Retourne un message de succès ou d'erreur."""
        try:
            fs_driver.append_text(path, content)
            return f"✓ Contenu ajouté à : {path}"
        except Exception as e:
            return f"⚠ Erreur ajout contenu à {path} : {str(e)}"
    
    def read_file(path: str) -> str:
        """Lit un fichier et retourne son contenu. Retourne un message d'erreur si échec."""
        try:
            content = fs_driver.read_text(path)
            return f"✓ Fichier lu ({len(content)} caractères) :\n\n{content}"
        except Exception as e:
            return f"⚠ Erreur lecture fichier {path} : {str(e)}"
    
    def move_path(src: str, dst: str) -> str:
        """Déplace/renomme un fichier ou dossier. Retourne un message de succès ou d'erreur."""
        try:
            fs_driver.move_path(src, dst, overwrite=False)
            return f"✓ Déplacé : {src} → {dst}"
        except Exception as e:
            return f"⚠ Erreur déplacement {src} → {dst} : {str(e)}"
    
    def delete_path(path: str) -> str:
        """Supprime un fichier ou dossier. Retourne un message de succès ou d'erreur."""
        try:
            fs_driver.delete_path(path)
            return f"✓ Supprimé : {path}"
        except Exception as e:
            return f"⚠ Erreur suppression {path} : {str(e)}"
    
    def list_dir(path: str = "") -> str:
        """Liste le contenu d'un dossier. Retourne une liste formatée ou un message d'erreur."""
        try:
            items = fs_driver.list_dir(path)
            if not items:
                return f"✓ Dossier vide : {path or '.'}"
            result = f"✓ {len(items)} élément(s) dans {path or '.'} :\n"
            for item in items[:50]:  # Limiter à 50 éléments
                item_type = "📁" if item.is_dir else "📄"
                size_info = f" ({item.size} octets)" if item.size else ""
                result += f"  {item_type} {item.path}{size_info}\n"
            return result
        except Exception as e:
            return f"⚠ Erreur listage {path} : {str(e)}"
    
    # Créer l'agent avec les tools
    # Note: Autogen utilise register_for_execution pour les fonctions
    fs_agent = AssistantAgent(
        name="fs_agent",
        system_message="""Tu es un agent spécialisé filesystem.
Tu ne réponds jamais directement à l'utilisateur.
Tu exécutes uniquement les actions demandées via tes tools,
et tu retournes des résultats structurés (succès/échec + détails).
Utilise les fonctions disponibles : create_dir, create_file, append_to_file, read_file, move_path, delete_path, list_dir.""",
        llm_config=llm_config,
    )
    
    # Note: Les fonctions seront appelées via le système de tools d'Autogen
    # Pour l'instant, on les expose via le system_message et l'agent les utilisera
    # si Autogen supporte l'appel de fonctions Python directement
    
    return fs_agent


def create_memory_agent(llm_config: Dict[str, Any], db_path: str = "memory/memory.sqlite") -> AssistantAgent:
    """Agent spécialisé mémoire. Wrappe MemoryCore."""
    # Initialiser la DB si nécessaire
    init_db(db_path=db_path)
    
    # Fonctions wrapper autour de MemoryCore
    def save_note_tool(content: str, tags: Optional[list] = None) -> str:
        """Enregistre une note. Retourne un message de succès ou d'erreur."""
        try:
            note_id = save_note(content, tags)
            return f"✓ Note sauvegardée (ID: {note_id})"
        except Exception as e:
            return f"⚠ Erreur sauvegarde note : {str(e)}"
    
    def list_notes() -> str:
        """Liste toutes les notes. Retourne une liste formatée."""
        try:
            notes = get_items(type="note")
            if not notes:
                return "✓ Aucune note trouvée"
            result = f"✓ {len(notes)} note(s) :\n"
            for note in notes:
                result += f"  - ID {note['id']}: {note['content'][:100]}...\n"
            return result
        except Exception as e:
            return f"⚠ Erreur listage notes : {str(e)}"
    
    def save_todo_tool(content: str, tags: Optional[list] = None) -> str:
        """Enregistre un todo. Retourne un message de succès ou d'erreur."""
        try:
            todo_id = save_todo(content, tags)
            return f"✓ Todo sauvegardé (ID: {todo_id})"
        except Exception as e:
            return f"⚠ Erreur sauvegarde todo : {str(e)}"
    
    def list_todos() -> str:
        """Liste tous les todos. Retourne une liste formatée."""
        try:
            todos = get_items(type="todo")
            if not todos:
                return "✓ Aucun todo trouvé"
            result = f"✓ {len(todos)} todo(s) :\n"
            for todo in todos:
                result += f"  - ID {todo['id']}: {todo['content'][:100]}...\n"
            return result
        except Exception as e:
            return f"⚠ Erreur listage todos : {str(e)}"
    
    def save_process_tool(content: str, tags: Optional[list] = None) -> str:
        """Enregistre un processus. Retourne un message de succès ou d'erreur."""
        try:
            process_id = save_process(content, tags)
            return f"✓ Processus sauvegardé (ID: {process_id})"
        except Exception as e:
            return f"⚠ Erreur sauvegarde processus : {str(e)}"
    
    def list_processes() -> str:
        """Liste tous les processus. Retourne une liste formatée."""
        try:
            processes = get_items(type="process")
            if not processes:
                return "✓ Aucun processus trouvé"
            result = f"✓ {len(processes)} processus :\n"
            for proc in processes:
                result += f"  - ID {proc['id']}: {proc['content'][:100]}...\n"
            return result
        except Exception as e:
            return f"⚠ Erreur listage processus : {str(e)}"
    
    def save_protocol_tool(content: str, tags: Optional[list] = None) -> str:
        """Enregistre un protocole. Retourne un message de succès ou d'erreur."""
        try:
            protocol_id = save_protocol(content, tags)
            return f"✓ Protocole sauvegardé (ID: {protocol_id})"
        except Exception as e:
            return f"⚠ Erreur sauvegarde protocole : {str(e)}"
    
    def list_protocols() -> str:
        """Liste tous les protocoles. Retourne une liste formatée."""
        try:
            protocols = get_items(type="protocol")
            if not protocols:
                return "✓ Aucun protocole trouvé"
            result = f"✓ {len(protocols)} protocole(s) :\n"
            for proto in protocols:
                result += f"  - ID {proto['id']}: {proto['content'][:100]}...\n"
            return result
        except Exception as e:
            return f"⚠ Erreur listage protocoles : {str(e)}"
    
    def save_preference_tool(key: str, value: str, scope: str = "global") -> str:
        """Enregistre une préférence. Retourne un message de succès ou d'erreur."""
        try:
            save_preference(key=key, value=value, scope=scope)
            return f"✓ Préférence sauvegardée : {key} = {value}"
        except Exception as e:
            return f"⚠ Erreur sauvegarde préférence : {str(e)}"
    
    def list_preferences_tool() -> str:
        """Liste toutes les préférences. Retourne une liste formatée."""
        try:
            prefs = list_preferences()
            if not prefs:
                return "✓ Aucune préférence trouvée"
            result = f"✓ {len(prefs)} préférence(s) :\n"
            for pref in prefs:
                result += f"  - {pref['key']} = {pref['value']} (scope: {pref.get('scope', 'global')})\n"
            return result
        except Exception as e:
            return f"⚠ Erreur listage préférences : {str(e)}"
    
    def search_memory(query: str) -> str:
        """Recherche dans la mémoire (notes, todos, processus, protocoles). Retourne les résultats."""
        try:
            results = search_items(query=query)
            if not results:
                return f"✓ Aucun résultat pour '{query}'"
            result = f"✓ {len(results)} résultat(s) pour '{query}' :\n"
            for item in results[:20]:  # Limiter à 20 résultats
                result += f"  - [{item['type']}] ID {item['id']}: {item['content'][:80]}...\n"
            return result
        except Exception as e:
            return f"⚠ Erreur recherche : {str(e)}"
    
    # Créer l'agent avec les tools
    memory_agent = AssistantAgent(
        name="memory_agent",
        system_message="""Tu es un agent spécialisé mémoire.
Tu ne réponds jamais directement à l'utilisateur.
Tu exécutes uniquement les actions demandées via tes tools,
et tu retournes des résultats structurés (succès/échec + détails).
Utilise les fonctions disponibles : save_note, list_notes, save_todo, list_todos, save_process, list_processes, save_protocol, list_protocols, save_preference, list_preferences, search_memory.""",
        llm_config=llm_config,
    )
    
    # Note: Les fonctions seront appelées via le système de tools d'Autogen
    # Pour l'instant, on les expose via le system_message et l'agent les utilisera
    # si Autogen supporte l'appel de fonctions Python directement
    
    return memory_agent


def create_interpreter_agent(
    llm_config: Dict[str, Any],
    fs_agent: AssistantAgent,
    memory_agent: AssistantAgent
) -> AssistantAgent:
    """Agent chef d'orchestre : parle à l'utilisateur et délègue."""
    
    interpreter = AssistantAgent(
        name="interpreter",
        system_message="""Tu es Clara, un agent technique et logique. Pas de psychologie, pas de thérapie.
Tu réponds court, net, analytique, sans blabla. Tu ne proposes pas d'options de conversation.
Tu ne fais pas semblant que l'utilisateur ne sait pas quoi dire.
Tu ne poses pas 10 questions si l'utilisateur n'écrit rien.
Tu ne continues pas le dialogue si aucun message n'est fourni.

Tu es un agent d'exécution pour Jérémy :
- Tu exécutes uniquement ce qui est demandé.
- Tu n'inventes rien.
- Tu ne fais pas de suggestions non sollicitées.
- Tu restes technique, précis, professionnel.

Si l'utilisateur écrit quelque chose → tu analyses et réponds.
Si l'utilisateur n'écrit rien → tu ne génères **aucune** réponse.

Tu peux appeler d'autres agents (fs_agent, memory_agent) quand c'est utile :
- De créer, lire, écrire, lister, déplacer ou supprimer des fichiers/dossiers → appelle fs_agent
- De sauvegarder, lister, rechercher des notes, todos, processus, protocoles, préférences → appelle memory_agent
- Une explication, une reformulation, ou une conversation générale → réponds directement""",
        llm_config=llm_config,
    )
    
    return interpreter

