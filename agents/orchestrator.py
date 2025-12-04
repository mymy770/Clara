# Clara - Orchestrateur central
"""
Orchestrateur principal de Clara
Gère la conversation, l'historique et appelle le LLM
"""

import yaml
from datetime import datetime
from drivers.llm_driver import LLMDriver
from memory.memory_core import MemoryCore
from utils.logger import DebugLogger


class Orchestrator:
    """Orchestrateur central de Clara"""
    
    def __init__(self, config_path="config/settings.yaml"):
        # Charger la configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Initialiser les composants
        self.llm_driver = LLMDriver(config_path)
        self.memory = MemoryCore(self.config.get('memory_db_path', 'memory/memory.sqlite'))
        
        # Historique de conversation (en mémoire)
        self.conversation_history = []
        self.max_history = self.config.get('max_history_messages', 20)
        
        # System prompt
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self):
        """Construit le prompt système de Clara"""
        return """Tu es Clara, une assistante IA intelligente et serviable.

Caractéristiques :
- Tu es courtoise et professionnelle
- Tu réponds de manière claire et concise
- Tu adaptes ta langue à celle de l'utilisateur
- Tu es honnête : si tu ne sais pas quelque chose, tu le dis

Pour l'instant, tu es en phase de construction (Phase 1).
Tu peux uniquement converser et répondre aux questions.
Tu n'as pas encore accès à des outils externes (fichiers, emails, etc.)."""
    
    def handle_message(self, user_message, session_id, debug_logger):
        """
        Traite un message utilisateur
        
        Args:
            user_message: Message de l'utilisateur
            session_id: ID de la session
            debug_logger: Logger de debug
        
        Returns:
            str: Réponse de Clara
        """
        try:
            # Ajouter le message utilisateur à l'historique
            self.conversation_history.append({
                'role': 'user',
                'content': user_message
            })
            
            # Construire les messages pour le LLM
            messages = self._build_prompt()
            
            # Appeler le LLM
            response = self.llm_driver.generate(messages)
            clara_response = response['text']
            
            # Ajouter la réponse à l'historique
            self.conversation_history.append({
                'role': 'assistant',
                'content': clara_response
            })
            
            # Limiter la taille de l'historique
            if len(self.conversation_history) > self.max_history:
                # Garder le system prompt et les N derniers messages
                self.conversation_history = self.conversation_history[-self.max_history:]
            
            # Logger le debug
            debug_logger.log_interaction(
                user_input=user_message,
                prompt_messages=messages,
                llm_response=clara_response,
                usage=response['usage'],
                error=None
            )
            
            # Sauvegarder dans la mémoire
            self.memory.save_interaction(session_id, user_message, clara_response)
            
            return clara_response
            
        except Exception as e:
            error_msg = f"Erreur : {str(e)}"
            
            # Logger l'erreur
            debug_logger.log_interaction(
                user_input=user_message,
                prompt_messages=messages if 'messages' in locals() else [],
                llm_response=None,
                usage=None,
                error=error_msg
            )
            
            return f"Désolée, j'ai rencontré une erreur : {str(e)}"
    
    def _build_prompt(self):
        """Construit le prompt complet avec system + historique"""
        messages = [
            {'role': 'system', 'content': self.system_prompt}
        ]
        
        # Ajouter l'historique
        messages.extend(self.conversation_history)
        
        return messages
    
    def load_session_context(self, session_id):
        """Charge le contexte d'une session existante"""
        context = self.memory.load_context(session_id, limit=self.max_history // 2)
        
        for user_msg, clara_msg in context:
            self.conversation_history.append({'role': 'user', 'content': user_msg})
            self.conversation_history.append({'role': 'assistant', 'content': clara_msg})
