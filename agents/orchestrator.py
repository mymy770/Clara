# Clara - Orchestrateur central
"""
Orchestrateur principal de Clara
Gère la conversation, l'historique et appelle le LLM
"""

import yaml
import json
import re
from datetime import datetime
from drivers.llm_driver import LLMDriver
from utils.logger import DebugLogger
from memory.helpers import save_note
from memory.memory_core import get_items, search_items, delete_item


class Orchestrator:
    """Orchestrateur central de Clara"""
    
    def __init__(self, config_path="config/settings.yaml"):
        # Charger la configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Initialiser les composants
        self.llm_driver = LLMDriver(config_path)
        
        # Historique de conversation (en mémoire RAM)
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

Capacités mémoire (Phase 3) :
Tu as maintenant accès à une mémoire persistante pour les notes.

Actions disponibles :
1. memory_save_note : Sauvegarder une note
2. memory_list_notes : Lister toutes les notes
3. memory_search_notes : Chercher dans les notes
4. memory_delete_item : Supprimer un élément par ID

Quand l'utilisateur te demande de sauvegarder, lister, chercher ou supprimer des notes,
tu dois RETOURNER une structure JSON d'intention dans ta réponse, délimitée par des balises :

```json
{"memory_action": "save_note", "content": "texte de la note", "tags": ["optionnel"]}
```

ou

```json
{"memory_action": "list_notes"}
```

ou

```json
{"memory_action": "search_notes", "query": "mot à chercher"}
```

ou

```json
{"memory_action": "delete_item", "item_id": 123}
```

IMPORTANT : Tu dois TOUJOURS répondre au format texte naturel à l'utilisateur, 
ET inclure le bloc JSON si une action mémoire est nécessaire.

Pour l'instant, tu es en phase de construction (Phase 3).
Tu peux converser et gérer des notes en mémoire.
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
            
            # Chercher une intention mémoire dans la réponse
            memory_result = self._process_memory_action(clara_response)
            
            # Si une action mémoire a été exécutée, ajouter le résultat à la réponse
            if memory_result:
                clara_response = self._clean_response(clara_response) + f"\n\n{memory_result}"
            
            # Ajouter la réponse à l'historique
            self.conversation_history.append({
                'role': 'assistant',
                'content': clara_response
            })
            
            # Limiter la taille de l'historique
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]
            
            # Logger le debug
            debug_logger.log_interaction(
                user_input=user_message,
                prompt_messages=messages,
                llm_response=clara_response,
                usage=response['usage'],
                error=None
            )
            
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
    
    def _process_memory_action(self, response_text):
        """
        Extrait et exécute une action mémoire depuis la réponse du LLM
        
        Returns:
            str: Message de résultat de l'action, ou None
        """
        try:
            # Chercher un bloc JSON dans la réponse
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if not json_match:
                return None
            
            # Parser le JSON
            intent = json.loads(json_match.group(1))
            action = intent.get('memory_action')
            
            if not action:
                return None
            
            # Exécuter l'action correspondante
            if action == 'save_note':
                content = intent.get('content', '')
                tags = intent.get('tags')
                item_id = save_note(content=content, tags=tags)
                return f"✓ Note sauvegardée (ID: {item_id})"
            
            elif action == 'list_notes':
                items = get_items(type='note', limit=50)
                if not items:
                    return "Aucune note en mémoire."
                result = f"📝 {len(items)} note(s) trouvée(s) :\n"
                for item in items[:10]:  # Limiter l'affichage à 10
                    result += f"  - ID {item['id']}: {item['content'][:50]}...\n"
                if len(items) > 10:
                    result += f"  ... et {len(items) - 10} autre(s)"
                return result
            
            elif action == 'search_notes':
                query = intent.get('query', '')
                items = search_items(type='note', query=query, limit=50)
                if not items:
                    return f"Aucune note trouvée pour '{query}'."
                result = f"🔍 {len(items)} note(s) trouvée(s) pour '{query}' :\n"
                for item in items[:10]:
                    result += f"  - ID {item['id']}: {item['content'][:50]}...\n"
                if len(items) > 10:
                    result += f"  ... et {len(items) - 10} autre(s)"
                return result
            
            elif action == 'delete_item':
                item_id = intent.get('item_id')
                if item_id:
                    delete_item(item_id=item_id)
                    return f"✓ Élément {item_id} supprimé"
                return "⚠ ID manquant pour la suppression"
            
            return None
            
        except (json.JSONDecodeError, Exception) as e:
            # En cas d'erreur de parsing ou d'exécution, ne pas planter
            return None
    
    def _clean_response(self, response_text):
        """Nettoie la réponse en enlevant le bloc JSON"""
        return re.sub(r'```json\s*\{.*?\}\s*```', '', response_text, flags=re.DOTALL).strip()
    
    def _build_prompt(self):
        """Construit le prompt complet avec system + historique"""
        messages = [
            {'role': 'system', 'content': self.system_prompt}
        ]
        
        # Ajouter l'historique
        messages.extend(self.conversation_history)
        
        return messages
