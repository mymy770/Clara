#!/usr/bin/env python3
# Clara - Point d'entrée principal
"""
Point d'entrée de Clara
Lance une session interactive avec l'utilisateur
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import Orchestrator
from utils.logger import SessionLogger, DebugLogger


def generate_session_id():
    """Génère un ID de session unique"""
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def main():
    """Fonction principale"""
    print("=" * 60)
    print("Clara - Assistant IA")
    print("=" * 60)
    print()
    
    try:
        # Générer un ID de session
        session_id = generate_session_id()
        print(f"Session ID: {session_id}")
        print()
        
        # Initialiser les loggers
        session_logger = SessionLogger(session_id)
        debug_logger = DebugLogger(session_id)
        
        # Initialiser l'orchestrateur
        print("Initialisation de Clara...")
        orchestrator = Orchestrator()
        print("✓ Clara est prête !")
        print()
        print("Tapez 'quit' ou 'exit' pour quitter.")
        print("-" * 60)
        print()
        
        # Boucle de conversation
        while True:
            try:
                # Lire l'input utilisateur
                user_input = input("Vous: ")
                
                # Commandes de sortie
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nAu revoir ! 👋")
                    break
                
                # Ignorer les inputs vides
                if not user_input.strip():
                    continue
                
                # Logger l'input
                session_logger.log_user(user_input)
                
                # Traiter le message
                response = orchestrator.handle_message(user_input, session_id, debug_logger)
                
                # Afficher la réponse
                print(f"\nClara: {response}\n")
                
                # Logger la réponse
                session_logger.log_clara(response)
                
            except KeyboardInterrupt:
                print("\n\nInterruption détectée.")
                print("Au revoir ! 👋")
                break
            except Exception as e:
                print(f"\nErreur: {str(e)}\n")
                continue
        
        print(f"\nSession terminée: {session_id}")
        print(f"Logs sauvegardés dans logs/sessions/{session_id}.txt")
        print(f"Debug sauvegardé dans logs/debug/{session_id}.json")
        
    except Exception as e:
        print(f"\nErreur lors du démarrage de Clara: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
