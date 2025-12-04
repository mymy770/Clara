#!/usr/bin/env python3
"""
Clara V3 - Point d'entrée principal
Lance Clara localement
"""

import sys
import logging
from pathlib import Path
import yaml
from datetime import datetime

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import ClaraOrchestrator
from agents.fs_agent import FSAgent
from drivers.fs_driver import FSDriver
from memory.memory_core import MemoryCore


def setup_logging(config: dict):
    """Configure le système de logging"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f"logs/clara_{datetime.now().strftime('%Y-%m-%d')}.log")
        ]
    )


def load_config(config_path: str = "config/settings.yaml") -> dict:
    """Charge la configuration depuis YAML"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    """Fonction principale"""
    print("=" * 60)
    print("Clara V3 - Assistant IA Intelligent")
    print("=" * 60)
    print()
    
    try:
        # Charger la configuration
        config = load_config()
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        logger.info("Starting Clara V3...")
        
        # Initialiser la mémoire
        memory = MemoryCore(db_path=config['paths']['memory_db'])
        logger.info("Memory Core initialized")
        
        # Initialiser les drivers
        fs_driver = FSDriver()
        logger.info("FS Driver initialized")
        
        # Initialiser les agents
        fs_agent = FSAgent(config={}, fs_driver=fs_driver)
        logger.info("FS Agent initialized")
        
        # Initialiser l'orchestrateur
        clara = ClaraOrchestrator(config=config)
        clara.register_agent("fs_agent", fs_agent)
        logger.info("Clara Orchestrator initialized")
        
        # Démarrer une session
        session_id = clara.start_session()
        print(f"\nSession démarrée : {session_id}")
        print("\nClara V3 est prête !")
        print("(Interface de chat à venir - Phase 1)")
        print("\nPour l'instant, Clara est en mode construction.")
        print("Consultez le README.md pour plus d'informations.")
        print()
        
        # Mode interactif simple (temporaire)
        print("Mode interactif basique (tapez 'quit' pour quitter):")
        while True:
            try:
                user_input = input("\nVous: ")
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                response = clara.process_message(user_input)
                print(f"Clara: {response}")
                
            except KeyboardInterrupt:
                break
        
        # Terminer la session
        clara.end_session()
        memory.close()
        logger.info("Clara V3 stopped")
        print("\nAu revoir !")
        
    except Exception as e:
        print(f"\nErreur lors du démarrage de Clara: {e}")
        logging.error(f"Startup error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

