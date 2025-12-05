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
from memory.helpers import save_note, save_todo, save_process, save_protocol
from memory.memory_core import get_items, search_items, delete_item, save_preference


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

Capacités mémoire (Phase 2.5) :
Tu as maintenant accès à une mémoire persistante pour plusieurs types d'informations.

Actions disponibles :

NOTES :
- memory_save_note : Sauvegarder une note
- memory_list_notes : Lister toutes les notes
- memory_search_notes : Chercher dans les notes

TODOS :
- memory_save_todo : Enregistrer un todo (chose à faire)
- memory_list_todos : Lister tous les todos
- memory_search_todos : Chercher dans les todos

PROCESS :
- memory_save_process : Enregistrer un processus/procédure détaillée
- memory_list_processes : Lister tous les processus

PROTOCOL :
- memory_save_protocol : Enregistrer un protocole/règle générale
- memory_list_protocols : Lister tous les protocoles

PRÉFÉRENCES :
- memory_set_preference : Enregistrer une préférence (langue, canal de communication, etc.)

GÉNÉRAL :
- memory_delete_item : Supprimer un élément par ID (tous types)

Quand l'utilisateur demande de sauvegarder/lister/chercher ces éléments,
OU quand il exprime une préférence ("je préfère", "désormais", "à partir de maintenant", "toujours", "ne jamais"),
tu dois RETOURNER une structure JSON d'intention dans ta réponse, délimitée par des balises :

```json
{"memory_action": "save_note", "content": "texte", "tags": ["optionnel"]}
```

ou

```json
{"memory_action": "save_todo", "content": "chose à faire", "tags": ["optionnel"]}
```

ou

```json
{"memory_action": "list_todos"}
```

ou

```json
{"memory_action": "search_notes", "query": "mot"}
```

ou

```json
{"memory_action": "delete_item", "item_id": 123}
```

IMPORTANT : Tu dois TOUJOURS répondre au format texte naturel à l'utilisateur, 
ET inclure le bloc JSON si une action mémoire est nécessaire.

Pour l'instant, tu es en phase de construction (Phase 2.5).
Tu peux converser et gérer des notes, todos, processus et protocoles en mémoire.
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
            # PRÉ-VÉRIFICATION : Détecter si c'est une demande de lecture mémoire
            memory_context = self._check_memory_read_intent(user_message)
            
            # Ajouter le message utilisateur à l'historique
            self.conversation_history.append({
                'role': 'user',
                'content': user_message
            })
            
            # Construire les messages pour le LLM
            messages = self._build_prompt()
            
            # Si on a un contexte mémoire, l'ajouter au prompt
            if memory_context:
                messages.append({
                    'role': 'system',
                    'content': f"DONNÉES MÉMOIRE RÉELLES :\n{memory_context}"
                })
            
            # Appeler le LLM
            response = self.llm_driver.generate(messages)
            clara_response = response['text']
            
            # Chercher une intention mémoire dans la réponse (pour les actions d'écriture)
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
                for item in items[:10]:
                    result += f"  - ID {item['id']}: {item['content'][:50]}...\n"
                if len(items) > 10:
                    result += f"  ... et {len(items) - 10} autre(s)"
                return result
            
            elif action == 'search_notes':
                query = intent.get('query', '')
                items = search_items(query=query, type='note', limit=50)
                if not items:
                    return f"Aucune note trouvée pour '{query}'."
                result = f"🔍 {len(items)} note(s) trouvée(s) pour '{query}' :\n"
                for item in items[:10]:
                    result += f"  - ID {item['id']}: {item['content'][:50]}...\n"
                if len(items) > 10:
                    result += f"  ... et {len(items) - 10} autre(s)"
                return result
            
            elif action == 'save_todo':
                content = intent.get('content', '')
                tags = intent.get('tags')
                item_id = save_todo(content=content, tags=tags)
                return f"✓ Todo sauvegardé (ID: {item_id})"
            
            elif action == 'list_todos':
                items = get_items(type='todo', limit=50)
                if not items:
                    return "Aucun todo en mémoire."
                result = f"✅ {len(items)} todo(s) trouvé(s) :\n"
                for item in items[:10]:
                    result += f"  - ID {item['id']}: {item['content'][:50]}...\n"
                if len(items) > 10:
                    result += f"  ... et {len(items) - 10} autre(s)"
                return result
            
            elif action == 'search_todos':
                query = intent.get('query', '')
                items = search_items(query=query, type='todo', limit=50)
                if not items:
                    return f"Aucun todo trouvé pour '{query}'."
                result = f"🔍 {len(items)} todo(s) trouvé(s) pour '{query}' :\n"
                for item in items[:10]:
                    result += f"  - ID {item['id']}: {item['content'][:50]}...\n"
                if len(items) > 10:
                    result += f"  ... et {len(items) - 10} autre(s)"
                return result
            
            elif action == 'save_process':
                content = intent.get('content', '')
                tags = intent.get('tags')
                item_id = save_process(content=content, tags=tags)
                return f"✓ Processus sauvegardé (ID: {item_id})"
            
            elif action == 'list_processes':
                items = get_items(type='process', limit=50)
                if not items:
                    return "Aucun processus en mémoire."
                result = f"⚙️ {len(items)} processus trouvé(s) :\n"
                for item in items[:10]:
                    result += f"  - ID {item['id']}: {item['content'][:80]}...\n"
                if len(items) > 10:
                    result += f"  ... et {len(items) - 10} autre(s)"
                return result
            
            elif action == 'save_protocol':
                content = intent.get('content', '')
                tags = intent.get('tags')
                item_id = save_protocol(content=content, tags=tags)
                return f"✓ Protocole sauvegardé (ID: {item_id})"
            
            elif action == 'list_protocols':
                items = get_items(type='protocol', limit=50)
                if not items:
                    return "Aucun protocole en mémoire."
                result = f"📋 {len(items)} protocole(s) trouvé(s) :\n"
                for item in items[:10]:
                    result += f"  - ID {item['id']}: {item['content'][:80]}...\n"
                if len(items) > 10:
                    result += f"  ... et {len(items) - 10} autre(s)"
                return result
            
            elif action == 'set_preference':
                pref_dict = {
                    'scope': intent.get('scope', 'global'),
                    'agent': intent.get('agent'),
                    'domain': intent.get('domain', 'general'),
                    'key': intent.get('key'),
                    'value': intent.get('value'),
                    'source': intent.get('source', 'user'),
                    'confidence': intent.get('confidence', 1.0)
                }
                if pref_dict['key'] and pref_dict['value']:
                    success = save_preference(pref_dict)
                    if success:
                        # Sauvegarder aussi dans memory avec tags
                        from memory.helpers import save_note
                        tags = ["preference", pref_dict.get('domain', 'general'), pref_dict.get('agent') or 'global']
                        save_note(f"Préférence: {pref_dict['key']} = {pref_dict['value']}", tags=tags)
                        return f"✓ Préférence enregistrée : {pref_dict['key']} = {pref_dict['value']}"
                    else:
                        return "⚠ Erreur lors de l'enregistrement de la préférence"
                return "⚠ Clé ou valeur manquante pour la préférence"
            
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
    
    def _check_memory_read_intent(self, user_message):
        """
        Pré-vérifie si le message demande une lecture mémoire
        Si oui, interroge la DB AVANT l'appel LLM pour éviter hallucinations
        
        Détecte aussi les intentions de préférences
        
        Returns:
            str: Contexte mémoire formaté, ou None
        """
        msg_lower = user_message.lower()
        
        # Détection des préférences
        preference_keywords = [
            'je préfère', 'je préférerais', 'préfère', 'préférerais',
            'désormais', 'à partir de maintenant', 'dorénavant',
            'toujours', 'jamais', 'ne jamais',
            'souhaite que', 'veux que'
        ]
        is_preference_intent = any(kw in msg_lower for kw in preference_keywords)
        
        if is_preference_intent:
            # Retourner un contexte pour aider le LLM à générer l'intention JSON
            return "L'utilisateur exprime une préférence. Génère une intention JSON avec memory_action='set_preference'."
        
        # Détection basique d'intentions de lecture
        keywords_list = ['montre', 'liste', 'affiche', 'voir', 'consulte', 'lis']
        keywords_search = ['cherche', 'trouve', 'recherche']
        
        is_list_intent = any(kw in msg_lower for kw in keywords_list)
        is_search_intent = any(kw in msg_lower for kw in keywords_search)
        
        if not (is_list_intent or is_search_intent):
            return None
        
        # Détecter le type demandé
        result_parts = []
        
        if 'note' in msg_lower:
            if is_search_intent:
                # Extraire le mot-clé de recherche (simpliste)
                words = msg_lower.split()
                query = ' '.join(words[-3:])  # Derniers mots comme approximation
                items = search_items(query=query, type='note', limit=20)
                result_parts.append(f"NOTES (recherche '{query}'): {len(items)} trouvée(s)")
            else:
                items = get_items(type='note', limit=20)
                result_parts.append(f"NOTES: {len(items)} en mémoire")
            
            for item in items[:5]:
                result_parts.append(f"  - ID {item['id']}: {item['content'][:60]}")
        
        if 'todo' in msg_lower:
            items = get_items(type='todo', limit=20)
            result_parts.append(f"TODOS: {len(items)} en mémoire")
            for item in items[:5]:
                result_parts.append(f"  - ID {item['id']}: {item['content'][:60]}")
        
        if 'process' in msg_lower or 'processus' in msg_lower or 'procédure' in msg_lower:
            items = get_items(type='process', limit=20)
            result_parts.append(f"PROCESSUS: {len(items)} en mémoire")
            for item in items[:5]:
                result_parts.append(f"  - ID {item['id']}: {item['content'][:60]}")
        
        if 'protocol' in msg_lower or 'protocole' in msg_lower:
            items = get_items(type='protocol', limit=20)
            result_parts.append(f"PROTOCOLES: {len(items)} en mémoire")
            for item in items[:5]:
                result_parts.append(f"  - ID {item['id']}: {item['content'][:60]}")
        
        if result_parts:
            return '\n'.join(result_parts)
        
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
