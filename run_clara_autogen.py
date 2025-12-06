# Clara - Mode Autogen (Multi-agents)
"""
Point d'entrée CLI pour tester Clara en mode Autogen (multi-agents).
Ne touche pas à l'UI ni à run_clara.py existant.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent
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
        
        # Créer un UserProxyAgent pour l'utilisateur
        user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",  # Mode automatique (pas d'input humain pendant l'exécution)
            max_consecutive_auto_reply=10,
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
                user_input = input("Vous: ").strip()
                
                if user_input.lower() in {"quit", "exit", "q"}:
                    print("\nAu revoir ! 👋")
                    break
                
                if not user_input:
                    continue
                
                # Initialiser les listes de tracking
                agents_called = []
                tools_called = []
                error = None
                final_response = ""
                
                try:
                    # Envoyer la requête à l'interpreter via user_proxy
                    # L'interpreter décidera d'appeler fs_agent ou memory_agent si nécessaire
                    chat_result = user_proxy.initiate_chat(
                        recipient=interpreter,
                        message=user_input,
                        max_turns=5,  # Limiter les tours pour éviter les boucles
                    )
                    
                    # Extraire la réponse finale
                    if chat_result.chat_history:
                        final_response = chat_result.chat_history[-1].get("content", "")
                    else:
                        final_response = "Aucune réponse générée"
                    
                    # Afficher la réponse
                    print(f"\nClara: {final_response}\n")
                    
                except Exception as e:
                    error = str(e)
                    print(f"\n⚠ Erreur : {error}\n")
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

