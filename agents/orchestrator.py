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
from memory.contacts import save_contact, update_contact, find_contacts, get_all_contacts
from agents.helpers import set_fs_driver, execute_fs_action
from drivers.fs_driver import FSDriver
from typing import Optional


class Orchestrator:
    """Orchestrateur central de Clara"""
    
    def __init__(self, config_path="config/settings.yaml", fs_driver: Optional[FSDriver] = None):
        # Charger la configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Initialiser les composants
        self.llm_driver = LLMDriver(config_path)
        
        # Initialiser le driver filesystem si fourni
        if fs_driver:
            set_fs_driver(fs_driver)
        
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

CONTACTS :
- memory_save_contact : Enregistrer un contact structuré
- memory_update_contact : Modifier un contact existant
- memory_list_contacts : Lister tous les contacts
- memory_search_contacts : Rechercher dans les contacts

Format JSON attendu pour save_contact :
```json
{"memory_action": "save_contact",
 "contact": {
    "first_name": "...",
    "last_name": "...",
    "aliases": ["..."],
    "phones": [{"number": "...", "label": "perso", "primary": true}],
    "emails": [{"address": "...", "label": "perso", "primary": true}],
    "relationship": "...",
    "category": "family" | "friend" | "client" | "supplier" | "other",
    "notes": ["..."],
    "company": "...",
    "role": "..."
  }}
```

Autres actions contacts :
```json
{"memory_action": "list_contacts"}
{"memory_action": "search_contacts", "query": "..."}
{"memory_action": "update_contact", "contact_id": 12, "updates": {...}}
```

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

FILESYSTEM :
Tu peux aussi utiliser le FILESYSTEM pour travailler avec des fichiers.

INTENT: "filesystem"
- Utilise-le quand tu dois lire, écrire, lister, créer, déplacer ou supprimer des fichiers/dossiers.

Structure JSON attendue:
{
  "intent": "filesystem",
  "action": "<nom_action>",
  "params": {
    ...
  }
}

Actions supportées :
- "read_text"      → lire un fichier texte
- "write_text"     → écrire un fichier texte (création ou écrasement)
- "append_text"    → ajouter du texte à la fin d'un fichier
- "list_dir"       → lister un dossier
- "make_dir"       → créer un dossier
- "move_path"      → déplacer/renommer un fichier ou dossier
- "delete_path"    → supprimer un fichier ou dossier
- "stat_path"      → obtenir des infos sur un chemin
- "search_text"    → rechercher un texte dans des fichiers

Exemples:
- Pour lire un fichier:
  {
    "intent": "filesystem",
    "action": "read_text",
    "params": { "path": "journal/dev_notes/..." }
  }

- Pour créer un rapport:
  1) construire le contenu du rapport dans ta réponse interne
  2) utiliser "write_text" pour l'enregistrer dans un fichier .md ou .txt

Pour l'instant, tu es en phase de construction (Phase 2.5).
Tu peux converser, gérer des notes/todos/processus/protocoles en mémoire, et travailler avec des fichiers."""
    
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
            llm_raw_response = response['text']  # Réponse brute du LLM
            
            # Chercher une intention mémoire dans la réponse (pour les actions d'écriture)
            cleaned_response, memory_result, memory_ops = self._process_memory_action(llm_raw_response)
            
            # Chercher une intention filesystem dans la réponse
            fs_cleaned_response, fs_result, fs_ops = self._process_filesystem_action(cleaned_response)
            
            # Combiner les opérations mémoire et filesystem pour SYNC
            all_ops = memory_ops + fs_ops
            
            # Si une action filesystem a été exécutée, utiliser la réponse nettoyée et ajouter le résultat
            if fs_result:
                clara_response = fs_cleaned_response + f"\n\n{fs_result}"
            elif memory_result:
                clara_response = cleaned_response + f"\n\n{memory_result}"
            else:
                clara_response = cleaned_response
            
            # Ajouter la réponse à l'historique
            self.conversation_history.append({
                'role': 'assistant',
                'content': clara_response
            })
            
            # Limiter la taille de l'historique
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]
            
            # Extraire les données internes pour l'UI (utiliser la réponse brute du LLM pour la réflexion)
            internal_data = self._extract_internal_data(
                llm_raw_response=llm_raw_response,
                memory_result=memory_result, 
                memory_ops=all_ops  # Inclure toutes les opérations (mémoire + FS)
            )
            
            # Logger le debug avec les données internes
            debug_logger.log_interaction(
                user_input=user_message,
                prompt_messages=messages,
                llm_response=clara_response,
                usage=response['usage'],
                error=None,
                internal_data=internal_data,
                memory_ops=all_ops  # Inclure toutes les opérations
            )
            
            # Retourner la réponse avec les données internes
            return {
                'response': clara_response,
                'internal': internal_data
            }
            
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
            
            # En cas d'erreur, retourner un dict aussi pour la cohérence
            return {
                'response': f"Désolée, j'ai rencontré une erreur : {str(e)}",
                'internal': {
                    'thoughts': None,
                    'todo': None,
                    'steps': None
                }
            }
    
    def _process_memory_action(self, response_text):
        """
        Extrait et exécute une action mémoire depuis la réponse du LLM
        
        Returns:
            tuple: (cleaned_response, result_message, memory_ops)
                - cleaned_response: Réponse nettoyée (sans JSON)
                - result_message: Message de résultat (ou None)
                - memory_ops: Liste des actions mémoire exécutées [{"action": "...", "result": "..."}]
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # 1) Essayer d'abord le cas idéal : ```json { ... } ```
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
            
            # 2) Si rien trouvé, accepter n'importe quel bloc ``` { ... } ```
            if not json_match:
                json_match = re.search(r"```\s*(\{.*?\})\s*```", response_text, re.DOTALL)
            
            raw_json = None
            fallback_match = None
            
            # 3) Si on a trouvé un bloc code, on récupère le JSON
            if json_match:
                raw_json = json_match.group(1)
            else:
                # 4) Fallback : chercher un objet JSON "nu" dans le texte
                fallback_match = re.search(r"(\{\s*\"memory_action\".*?\})", response_text, re.DOTALL)
                if fallback_match:
                    raw_json = fallback_match.group(1)
            
            # Si on n'a toujours rien, on abandonne proprement
            if not raw_json:
                return (response_text, None, [])
            
            # Parser le JSON
            try:
                intent = json.loads(raw_json)
            except json.JSONDecodeError as e:
                logger.warning(f"Erreur parsing JSON: {e}, raw_json = {raw_json[:200]}")
                return (response_text, None, [])
            
            action = intent.get('memory_action')
            
            if not action:
                return (response_text, None, [])
            
            # Exécuter l'action correspondante
            result_message = None
            memory_ops = []
            
            if action == 'save_note':
                try:
                    content = intent.get('content', '')
                    tags = intent.get('tags')
                    item_id = save_note(content=content, tags=tags)
                    result_message = f"✓ Note sauvegardée (ID: {item_id})"
                    memory_ops.append({"action": "save_note", "result": "success", "item_id": item_id})
                except Exception as e:
                    logger.error(f"Erreur dans save_note: {e}", exc_info=True)
                    result_message = f"⚠ Erreur lors de la sauvegarde: {str(e)}"
                    memory_ops.append({"action": "save_note", "result": "error", "error": str(e)})
            
            elif action == 'list_notes':
                items = get_items(type='note', limit=50)
                if not items:
                    result_message = "Aucune note en mémoire."
                    memory_ops.append({"action": "list_notes", "result": "empty"})
                else:
                    result = f"📝 {len(items)} note(s) trouvée(s) :\n"
                    for item in items[:10]:
                        result += f"  - ID {item['id']}: {item['content'][:50]}...\n"
                    if len(items) > 10:
                        result += f"  ... et {len(items) - 10} autre(s)"
                    result_message = result
                    memory_ops.append({"action": "list_notes", "result": "success", "count": len(items)})
            
            elif action == 'search_notes':
                query = intent.get('query', '')
                items = search_items(query=query, type='note', limit=50)
                if not items:
                    result_message = f"Aucune note trouvée pour '{query}'."
                else:
                    result = f"🔍 {len(items)} note(s) trouvée(s) pour '{query}' :\n"
                    for item in items[:10]:
                        result += f"  - ID {item['id']}: {item['content'][:50]}...\n"
                    if len(items) > 10:
                        result += f"  ... et {len(items) - 10} autre(s)"
                    result_message = result
            
            elif action == 'save_todo':
                content = intent.get('content', '')
                tags = intent.get('tags')
                item_id = save_todo(content=content, tags=tags)
                result_message = f"✓ Todo sauvegardé (ID: {item_id})"
            
            elif action == 'list_todos':
                items = get_items(type='todo', limit=50)
                if not items:
                    result_message = "Aucun todo en mémoire."
                else:
                    result = f"✅ {len(items)} todo(s) trouvé(s) :\n"
                    for item in items[:10]:
                        result += f"  - ID {item['id']}: {item['content'][:50]}...\n"
                    if len(items) > 10:
                        result += f"  ... et {len(items) - 10} autre(s)"
                    result_message = result
            
            elif action == 'search_todos':
                query = intent.get('query', '')
                items = search_items(query=query, type='todo', limit=50)
                if not items:
                    result_message = f"Aucun todo trouvé pour '{query}'."
                else:
                    result = f"🔍 {len(items)} todo(s) trouvé(s) pour '{query}' :\n"
                    for item in items[:10]:
                        result += f"  - ID {item['id']}: {item['content'][:50]}...\n"
                    if len(items) > 10:
                        result += f"  ... et {len(items) - 10} autre(s)"
                    result_message = result
            
            elif action == 'save_process':
                content = intent.get('content', '')
                tags = intent.get('tags')
                item_id = save_process(content=content, tags=tags)
                result_message = f"✓ Processus sauvegardé (ID: {item_id})"
            
            elif action == 'list_processes':
                items = get_items(type='process', limit=50)
                if not items:
                    result_message = "Aucun processus en mémoire."
                else:
                    result = f"⚙️ {len(items)} processus trouvé(s) :\n"
                    for item in items[:10]:
                        result += f"  - ID {item['id']}: {item['content'][:80]}...\n"
                    if len(items) > 10:
                        result += f"  ... et {len(items) - 10} autre(s)"
                    result_message = result
            
            elif action == 'save_protocol':
                content = intent.get('content', '')
                tags = intent.get('tags')
                item_id = save_protocol(content=content, tags=tags)
                result_message = f"✓ Protocole sauvegardé (ID: {item_id})"
            
            elif action == 'list_protocols':
                items = get_items(type='protocol', limit=50)
                if not items:
                    result_message = "Aucun protocole en mémoire."
                else:
                    result = f"📋 {len(items)} protocole(s) trouvé(s) :\n"
                    for item in items[:10]:
                        result += f"  - ID {item['id']}: {item['content'][:80]}...\n"
                    if len(items) > 10:
                        result += f"  ... et {len(items) - 10} autre(s)"
                    result_message = result
            
            elif action == 'save_contact':
                contact = intent.get('contact')
                if contact:
                    item_id = save_contact(contact)
                    result_message = f"✓ Contact sauvegardé (ID: {item_id})"
                else:
                    result_message = "⚠ Données contact manquantes"
            
            elif action == 'update_contact':
                contact_id = intent.get('contact_id')
                updates = intent.get('updates', {})
                if contact_id and updates:
                    try:
                        update_contact(contact_id, updates)
                        result_message = f"✓ Contact mis à jour (ID: {contact_id})"
                    except ValueError as e:
                        result_message = f"⚠ {str(e)}"
                else:
                    result_message = "⚠ ID ou updates manquants"
            
            elif action == 'list_contacts':
                contacts = get_all_contacts(limit=50)
                if not contacts:
                    result_message = "Aucun contact en mémoire."
                else:
                    result = f"📇 {len(contacts)} contact(s) trouvé(s) :\n"
                    for contact in contacts[:10]:
                        name = contact.get('display_name', f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip())
                        if not name:
                            name = "Sans nom"
                        result += f"  - ID {contact.get('id')}: {name}\n"
                    if len(contacts) > 10:
                        result += f"  ... et {len(contacts) - 10} autre(s)"
                    result_message = result
            
            elif action == 'search_contacts':
                query = intent.get('query', '')
                if query:
                    results = find_contacts(query)
                    if not results:
                        result_message = f"Aucun contact trouvé pour '{query}'."
                    else:
                        result = f"🔍 {len(results)} contact(s) trouvé(s) pour '{query}' :\n"
                        for contact in results[:10]:
                            name = contact.get('display_name', f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip())
                            if not name:
                                name = "Sans nom"
                            result += f"  - ID {contact.get('id')}: {name}\n"
                        if len(results) > 10:
                            result += f"  ... et {len(results) - 10} autre(s)"
                        result_message = result
                else:
                    result_message = "⚠ Query manquante pour la recherche"
            
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
                        tags = ["preference", pref_dict.get('domain', 'general'), pref_dict.get('agent') or 'global']
                        save_note(f"Préférence: {pref_dict['key']} = {pref_dict['value']}", tags=tags)
                        result_message = f"✓ Préférence enregistrée : {pref_dict['key']} = {pref_dict['value']}"
                    else:
                        result_message = "⚠ Erreur lors de l'enregistrement de la préférence"
                else:
                    result_message = "⚠ Clé ou valeur manquante pour la préférence"
            
            elif action == 'delete_item':
                item_id = intent.get('item_id')
                if item_id:
                    delete_item(item_id=item_id)
                    result_message = f"✓ Élément {item_id} supprimé"
                else:
                    result_message = "⚠ ID manquant pour la suppression"
            else:
                return (response_text, None, [])
            
            # Si aucune action n'a été exécutée, retourner la réponse originale
            if result_message is None:
                return (response_text, None, [])
            
            # Ajouter l'action à memory_ops si pas déjà fait
            if not memory_ops:
                memory_ops.append({
                    "action": action,
                    "result": "success" if "✓" in result_message or "trouvé" in result_message.lower() else ("error" if "⚠" in result_message else "info"),
                    "message": result_message
                })
            
            # Nettoyage : on retire le bloc JSON de la réponse utilisateur
            try:
                if json_match:
                    cleaned = response_text.replace(json_match.group(0), "").strip()
                else:
                    # Fallback : si on a utilisé fallback_match, on enlève juste le JSON nu
                    if fallback_match:
                        cleaned = response_text.replace(fallback_match.group(1), "").strip()
                    else:
                        cleaned = response_text
            except Exception:
                cleaned = response_text
            
            # Logging optionnel
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"memory_action_executed: action={action}, raw_json={raw_json[:100] if len(raw_json) > 100 else raw_json}...")
            
            return (cleaned or "C'est enregistré.", result_message, memory_ops)
            
        except (json.JSONDecodeError, Exception) as e:
            # En cas d'erreur de parsing ou d'exécution, ne pas planter
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Erreur dans _process_memory_action: {e}")
            return (response_text, None, [])
    
    def _process_filesystem_action(self, response_text):
        """
        Extrait et exécute une action filesystem depuis la réponse du LLM
        
        Returns:
            tuple: (cleaned_response, result_message, fs_ops) ou (response_text, None, []) si pas d'action
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Chercher un bloc JSON avec intent="filesystem"
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
            if not json_match:
                json_match = re.search(r"```\s*(\{.*?\})\s*```", response_text, re.DOTALL)
            if not json_match:
                fallback_match = re.search(r"(\{\s*\"intent\".*?\})", response_text, re.DOTALL)
                if fallback_match:
                    raw_json = fallback_match.group(1)
                else:
                    return (response_text, None, [])
            else:
                raw_json = json_match.group(1)
            
            # Parser le JSON
            try:
                intent_data = json.loads(raw_json)
            except json.JSONDecodeError as e:
                logger.warning(f"Erreur parsing JSON filesystem: {e}")
                return (response_text, None, [])
            
            intent = intent_data.get('intent')
            if intent != 'filesystem':
                return (response_text, None, [])
            
            action = intent_data.get('action')
            params = intent_data.get('params', {})
            
            if not action:
                return (response_text, None, [])
            
            # Créer une entrée pour SYNC
            fs_ops = [{
                "action": f"FS {action}",
                "result": "success",
                "path": params.get('path', params.get('src', 'N/A'))
            }]
            
            # Exécuter l'action filesystem
            fs_result = execute_fs_action(action, params)
            
            if fs_result.get('ok'):
                # Construire un message lisible pour l'utilisateur avec les résultats réels
                if action == 'read_text':
                    content = fs_result.get('content', '')
                    # Inclure le contenu réel dans la réponse
                    result_message = f"✓ Fichier lu ({len(content)} caractères) :\n\n{content}"
                elif action == 'write_text':
                    result_message = f"✓ Fichier écrit : {params.get('path', '')}"
                elif action == 'append_text':
                    result_message = f"✓ Contenu ajouté à : {params.get('path', '')}"
                elif action == 'list_dir':
                    items = fs_result.get('items', [])
                    if items:
                        result_message = f"✓ {len(items)} élément(s) trouvé(s) :\n"
                        for item in items[:20]:  # Limiter à 20 pour la lisibilité
                            item_type = "📁" if item.get('is_dir') else "📄"
                            result_message += f"  {item_type} {item.get('path', '')}\n"
                    else:
                        result_message = f"✓ Dossier vide : {params.get('path', '.')}"
                elif action == 'make_dir':
                    result_message = f"✓ Dossier créé : {params.get('path', '')}"
                elif action == 'move_path':
                    result_message = f"✓ Déplacé : {params.get('src', '')} → {params.get('dst', '')}"
                elif action == 'delete_path':
                    result_message = f"✓ Supprimé : {params.get('path', '')}"
                elif action == 'stat_path':
                    info = fs_result.get('info', {})
                    if info.get('exists'):
                        size = info.get('size', 'N/A')
                        is_dir = "dossier" if info.get('is_dir') else "fichier"
                        result_message = f"✓ {is_dir.capitalize()} : {params.get('path', '')} ({size} octets)"
                    else:
                        result_message = f"⚠ Fichier introuvable : {params.get('path', '')}"
                elif action == 'search_text':
                    results = fs_result.get('results', [])
                    if results:
                        result_message = f"✓ {len(results)} résultat(s) trouvé(s) :\n"
                        for r in results[:10]:  # Limiter à 10 résultats
                            result_message += f"  📄 {r.get('path', '')} : {r.get('snippet', '')[:80]}...\n"
                    else:
                        result_message = f"✓ Aucun résultat trouvé pour '{params.get('query', '')}'"
                else:
                    result_message = fs_result.get('message', '✓ Action filesystem exécutée')
            else:
                error = fs_result.get('error', 'Erreur inconnue')
                result_message = f"⚠ Erreur filesystem : {error}"
            
            # Nettoyer la réponse (enlever le bloc JSON)
            if json_match:
                cleaned = response_text.replace(json_match.group(0), "").strip()
            elif 'fallback_match' in locals() and fallback_match:
                cleaned = response_text.replace(fallback_match.group(1), "").strip()
            else:
                cleaned = response_text
            
            logger.info(f"filesystem_action_executed: action={action}, path={params.get('path', 'N/A')}")
            
            return (cleaned, result_message, fs_ops)
            
        except Exception as e:
            logger.warning(f"Erreur dans _process_filesystem_action: {e}")
            return (response_text, None, [])
    
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
        
        # Détection des contacts
        contact_keywords = ['contact', 'numéro', 'email', 'téléphone', 'téléphone', 'phone']
        is_contact_intent = any(kw in msg_lower for kw in contact_keywords)
        
        if is_contact_intent and (is_list_intent or is_search_intent):
            # Interroger la DB AVANT l'appel LLM
            contacts = get_all_contacts(limit=20)
            if contacts:
                context = f"CONTACTS ENREGISTRÉS ({len(contacts)} trouvé(s)) :\n"
                for contact in contacts[:10]:
                    name = contact.get('display_name', f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip())
                    if not name:
                        name = "Sans nom"
                    phones = contact.get('phones', [])
                    emails = contact.get('emails', [])
                    context += f"- ID {contact.get('id')}: {name}"
                    if phones:
                        primary_phone = next((p for p in phones if p.get('primary')), phones[0])
                        context += f" | Tél: {primary_phone.get('number', 'N/A')}"
                    if emails:
                        primary_email = next((e for e in emails if e.get('primary')), emails[0])
                        context += f" | Email: {primary_email.get('address', 'N/A')}"
                    context += "\n"
                return context
            else:
                return "CONTACTS: Aucun contact enregistré."
        
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
    
    def _extract_internal_data(self, llm_raw_response, memory_result, memory_ops):
        """
        Extrait les données internes pour l'UI (réflexion, plan, étapes)
        
        Args:
            llm_raw_response: Réponse brute du LLM (avant nettoyage)
            memory_result: Résultat de l'action mémoire (si exécutée)
            memory_ops: Liste des actions mémoire exécutées
        
        Returns:
            dict: {
                'thoughts': str ou None,  # Réflexion : ce que le LLM a compris
                'todo': str ou None,      # Plan d'action : nombre d'étapes
                'steps': list ou None     # Observe : résultat final
            }
        """
        internal = {
            'thoughts': None,
            'todo': None,
            'steps': None
        }
        
        # THINK : Réflexion - extraire depuis la réponse brute du LLM
        # Prendre les premières lignes avant le JSON (si présent)
        if llm_raw_response:
            lines = llm_raw_response.split('\n')
            # Chercher le début du JSON pour s'arrêter avant
            reflection_lines = []
            for line in lines:
                if '```json' in line or line.strip().startswith('{') and '"memory_action"' in line:
                    break
                reflection_lines.append(line)
            
            # Prendre les 2-3 premières lignes significatives
            reflection = '\n'.join(reflection_lines[:3]).strip()
            if reflection:
                internal['thoughts'] = reflection
        
        # PLAN/TODO : Nombre d'étapes du plan
        if memory_ops:
            step_count = len(memory_ops)
            if step_count > 0:
                internal['todo'] = f"{step_count} étape(s)"
        
        # OBSERVE/SYNC : Résultat final + opérations exécutées
        steps_list = []
        
        # Ajouter les opérations mémoire
        if memory_ops:
            for op in memory_ops:
                action_name = op.get('action', 'action')
                result = op.get('result', 'success')
                if result == 'success':
                    steps_list.append(f"✓ {action_name}")
                else:
                    steps_list.append(f"⚠ {action_name}: {op.get('error', 'erreur')}")
        
        # Si pas d'opérations mais une réponse, indiquer que la réponse a été envoyée
        if not steps_list:
            if llm_raw_response:
                steps_list.append("✓ Réponse envoyée")
        
        if steps_list:
            internal['steps'] = steps_list
        
        return internal
    
    def _build_prompt(self):
        """Construit le prompt complet avec system + historique"""
        messages = [
            {'role': 'system', 'content': self.system_prompt}
        ]
        
        # Ajouter l'historique
        messages.extend(self.conversation_history)
        
        return messages
