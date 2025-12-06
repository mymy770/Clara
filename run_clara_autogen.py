# Clara - Mode Autogen (Multi-agents)
"""
Point d'entrée CLI pour tester Clara en mode Autogen (multi-agents).
Ne touche pas à l'UI ni à run_clara.py existant.
"""

# Supprimer les warnings Pydantic d'Autogen avant tout import
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    # Désactiver comportements automatiques d'Autogen (si settings existe)
    try:
        from autogen import settings
        settings.disable_telemetry = True
        settings.allow_non_api_models = True
    except (ImportError, AttributeError):
        # settings n'existe pas dans toutes les versions d'Autogen, on continue
        pass
except ImportError:
    print("❌ pyautogen n'est pas installé.")
    print("   Installez-le avec: pip install pyautogen")
    exit(1)

from agents.autogen_hub import (
    build_llm_config,
    create_fs_agent,
    create_memory_agent,
    create_interpreter_agent,
)


def generate_session_id() -> str:
    """Génère un ID de session unique"""
    return f"autogen_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def log_autogen_interaction(session_id: str, user_input: str, agents_called: list, tools_called: list, 
                           error: Optional[str], final_response: str):
    """Log minimal pour le mode Autogen"""
    log_dir = Path("logs/sessions")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{session_id}.jsonl"
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "agents_called": agents_called,
        "tools_called": tools_called,
        "error": error,
        "final_response": final_response,
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    """Point d'entrée principal"""
    print("🚀 Initialisation de Clara Autogen...")
    
    try:
        # Construire la config LLM
        llm_config = build_llm_config()
        print("✓ Config LLM chargée")
        
        # Créer les agents
        workspace_root = Path(__file__).resolve().parent
        fs_agent = create_fs_agent(llm_config, workspace_root)
        print("✓ FSAgent créé")
        
        memory_agent = create_memory_agent(llm_config)
        print("✓ MemoryAgent créé")
        
        interpreter = create_interpreter_agent(llm_config, fs_agent, memory_agent)
        print("✓ InterpreterAgent créé")
        
        # Créer un GroupChat pour permettre la communication entre agents
        groupchat = GroupChat(
            agents=[interpreter, fs_agent, memory_agent],
            messages=[],
            max_round=3,  # Limiter les tours pour éviter les boucles
        )
        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config=llm_config,
        )
        print("✓ GroupChat créé")
        
        # Créer un UserProxyAgent pour l'utilisateur
        user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",  # Mode automatique (pas d'input humain pendant l'exécution)
            max_consecutive_auto_reply=1,  # 1 seule réponse automatique
            code_execution_config=False,  # Pas d'exécution de code pour l'instant
        )
        
        # Configurer la communication : l'interpreter peut parler à fs_agent et memory_agent
        # Le user_proxy parle à l'interpreter
        
        session_id = generate_session_id()
        print(f"✓ Session créée : {session_id}")
        print()
        print("=" * 60)
        print("Clara Autogen - Mode terminal")
        print("Tapez 'quit' ou 'exit' pour sortir.")
        print("=" * 60)
        print()
        
        while True:
            try:
                user_input = input("\nVous: ").strip()
                
                # 1 — Quit
                if user_input.lower() in {"quit", "exit"}:
                    print("🔚 Fermeture de Clara Autogen.")
                    break
                
                # 2 — Input vide = ne rien envoyer au modèle
                if user_input == "":
                    print("(aucune entrée détectée)")
                    continue
                
                # Initialiser les listes de tracking
                agents_called = []
                tools_called = []
                error = None
                final_response = ""
                
                # 3 — Envoyer au user_proxy / interpreter avec un nombre de tours limité
                try:
                    # Capturer stdout/stderr pour supprimer tous les messages verbeux d'Autogen
                    import sys
                    from io import StringIO
                    old_stdout = sys.stdout
                    old_stderr = sys.stderr
                    sys.stdout = StringIO()
                    sys.stderr = StringIO()
                    
                    # Utiliser le GroupChatManager au lieu de l'interpreter directement
                    response = user_proxy.initiate_chat(
                        manager,
                        message=user_input,
                        max_turns=2,  # 2 tours pour permettre la délégation aux agents spécialisés
                        silent=True,  # Désactiver l'affichage verbeux des échanges inter-agents
                    )
                    
                    # Restaurer stdout/stderr
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                    
                    # Extraire la réponse du GroupChatManager
                    # Le GroupChatManager stocke les messages dans groupchat.messages
                    final_response = ""
                    if hasattr(manager, "groupchat") and hasattr(manager.groupchat, "messages") and manager.groupchat.messages:
                        # Chercher le dernier message de l'interpreter avec du contenu (pas vide)
                        for msg in reversed(manager.groupchat.messages):
                            # Les messages sont des objets avec des attributs name et content
                            if hasattr(msg, "name") and msg.name == "interpreter":
                                if hasattr(msg, "content") and msg.content and msg.content.strip():
                                    final_response = msg.content.strip()
                                    break
                            # Fallback: si c'est un dict
                            elif isinstance(msg, dict) and msg.get("name") == "interpreter":
                                content = msg.get("content", "")
                                if content and content.strip():
                                    final_response = content.strip()
                                    break
                        
                        # Si pas de message de l'interpreter avec contenu, prendre le dernier message non-user avec contenu
                        if not final_response:
                            for msg in reversed(manager.groupchat.messages):
                                if hasattr(msg, "name") and msg.name != "user_proxy":
                                    if hasattr(msg, "content") and msg.content and msg.content.strip():
                                        final_response = msg.content.strip()
                                        break
                                elif isinstance(msg, dict) and msg.get("name") != "user_proxy":
                                    content = msg.get("content", "")
                                    if content and content.strip():
                                        final_response = content.strip()
                                        break
                    
                    # Fallbacks
                    if not final_response:
                        if hasattr(response, "summary") and response.summary:
                            final_response = response.summary
                        elif hasattr(response, "chat_history") and response.chat_history:
                            # Chercher le dernier message avec contenu dans chat_history
                            for msg in reversed(response.chat_history):
                                if isinstance(msg, dict):
                                    content = msg.get("content", "")
                                    if content and content.strip():
                                        final_response = content.strip()
                                        break
                                else:
                                    content = str(msg)
                                    if content and content.strip():
                                        final_response = content.strip()
                                        break
                    
                    if not final_response:
                        final_response = "(pas de réponse)"
                    print("\nClara:", final_response)
                    
                except Exception as e:
                    error = str(e)
                    print(f"❌ Erreur Autogen: {e}")
                    final_response = f"Erreur : {error}"
                
                # Logger l'interaction
                log_autogen_interaction(
                    session_id=session_id,
                    user_input=user_input,
                    agents_called=agents_called,
                    tools_called=tools_called,
                    error=error,
                    final_response=final_response,
                )
                
            except KeyboardInterrupt:
                print("\n\nInterruption détectée.")
                break
            except Exception as e:
                print(f"\n⚠ Erreur inattendue : {e}\n")
    
    except Exception as e:
        print(f"\n❌ Erreur lors de l'initialisation : {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()

