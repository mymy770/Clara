############################################
# PHASE 3.5 – ÉTENDRE LA MÉMOIRE :
# TODO / PROCESS / PROTOCOL
# Fichier recommandé : gpt_cursor/2025-12-05_phase3_5_memory_todo_process_protocol.md
############################################

🎯 OBJECTIF
Étendre la mémoire existante (déjà fonctionnelle pour les notes) aux types :
- todo
- process
- protocol

Sans changer l’architecture, sans ajouter de logique magique,
en réutilisant le même pattern que pour les notes.

On NE touche PAS encore aux contacts dans cette phase.

============================================
1. CONTRAINTES GÉNÉRALES
============================================

1) Ne pas modifier la structure SQL de base si ce n’est pas nécessaire.
   On reste sur la même table `memory` avec colonne `type`.

2) Ne pas ajouter de logique métier complexe dans memory_core.py.
   C’est juste une couche d’accès / helpers.

3) Ne pas mélanger cette phase avec :
   - drivers mail / calendar / whatsapp
   - Autogen ou multi-agents
   - gestion des contacts structurés

4) On reste sur le même style que notes :
   - intentions JSON simples
   - mapping propre dans orchestrator
   - logs cohérents

============================================
2. MEMORY CORE / HELPERS
============================================

Fichiers concernés :
- memory/memory_core.py
- memory/helpers.py

2.1. Vérifier que save_item / get_items / search_items / delete_item
     sont bien génériques (déjà fait en Phase 3).

2.2. Compléter / créer les helpers dans memory/helpers.py :

Ajouter, si absent :

    def save_todo(content: str, tags: list[str] | None = None) -> int:
        """Enregistre un todo dans la mémoire (type='todo')."""
        return save_item("todo", content, tags)

    def save_process(content: str, tags: list[str] | None = None) -> int:
        """Enregistre un process dans la mémoire (type='process')."""
        return save_item("process", content, tags)

    def save_protocol(content: str, tags: list[str] | None = None) -> int:
        """Enregistre un protocole dans la mémoire (type='protocol')."""
        return save_item("protocol", content, tags)

Optionnel si utile pour orchestrator (mais rester simple) :

    def list_todos(limit: int = 50):
        return get_items("todo", limit=limit)

    def list_processes(limit: int = 50):
        return get_items("process", limit=limit)

    def list_protocols(limit: int = 50):
        return get_items("protocol", limit=limit)

    def search_todos(query: str, limit: int = 50):
        return search_items("todo", query, limit=limit)

    # etc. si vraiment nécessaire

============================================
3. ORCHESTRATOR – INTENTIONS TODO / PROCESS / PROTOCOL
============================================

Fichier : agents/orchestrator.py

Objectif : réutiliser EXACTEMENT le même pattern que pour les notes,
mais en l’étendant à trois nouveaux types.

3.1. Imports

Compléter les imports pour utiliser les helpers :

    from memory.helpers import (
        save_note,
        save_todo,
        save_process,
        save_protocol,
        # et éventuellement list_* si créés
    )
    from memory.memory_core import get_items, search_items, delete_item

Adapter à l’existant (ne pas dupliquer les imports déjà présents).

3.2. Intentions mémoire côté LLM

Dans le prompt système ou le bloc d’instructions que tu utilises POUR le LLM
(phase 3 l’a déjà fait pour les notes), étendre la description des capacités mémoire.

Le LLM doit connaître les actions possibles, par exemple :

- memory_save_note
- memory_list_notes
- memory_search_notes
- memory_delete_item

Étendre avec :

- memory_save_todo
- memory_list_todos
- memory_search_todos

- memory_save_process
- memory_list_processes

- memory_save_protocol
- memory_list_protocols

Règles générales à préciser dans le prompt :
- Quand l’utilisateur demande d’enregistrer “quelque chose à faire” → proposer un `memory_save_todo`.
- Quand il demande “un process” (procédure détaillée) → `memory_save_process`.
- Quand il parle de “protocole” (règles générales) → `memory_save_protocol`.
- Quand il demande à revoir ces éléments → utiliser les actions list_* / search_* côté LLM.

Le format de l’intention JSON doit rester cohérent avec la Phase 3, par exemple :

    {
      "memory_action": "save_todo",
      "content": "Appeler le fournisseur pour vérifier les stocks",
      "tags": ["fournisseur", "urgent"]
    }

ou

    {
      "memory_action": "list_todos"
    }

3.3. Parsing et routing côté orchestrator

Dans la partie de orchestrator qui :
- reçoit la réponse brute du LLM
- extrait et parse le JSON d’intention

Étendre le switch / if existant pour gérer les nouveaux cas,
par exemple (pseudo-code, à adapter au code réel) :

    if intent["memory_action"] == "save_note":
        note_id = save_note(intent["content"], intent.get("tags"))
        # enrichir la réponse avec l’id créé

    elif intent["memory_action"] == "save_todo":
        todo_id = save_todo(intent["content"], intent.get("tags"))
        # enrichir la réponse avec l’id créé

    elif intent["memory_action"] == "list_todos":
        todos = get_items("todo", limit=50)
        # formater une petite liste lisible pour le user

    elif intent["memory_action"] == "save_process":
        process_id = save_process(intent["content"], intent.get("tags"))

    elif intent["memory_action"] == "list_processes":
        processes = get_items("process", limit=50)

    elif intent["memory_action"] == "save_protocol":
        protocol_id = save_protocol(intent["content"], intent.get("tags"))

    elif intent["memory_action"] == "list_protocols":
        protocols = get_items("protocol", limit=limit)

    elif intent["memory_action"] == "delete_item":
        delete_item(intent["id"])

Important :
- Gérer proprement le cas où le JSON est absent ou mal formé → dans ce cas, on n’exécute rien, on répond juste en texte.
- Ne PAS planter l’orchestrator si l’intention est inconnue → log + ignorer.

3.4. Logging

Pour CHAQUE action mémoire exécutée via ces intentions, logguer dans le debug JSON :

- "action": "memory.save_todo" / "memory.list_todos" / etc.
- "params": {...}
- "result": (id créé, nombre d’items, etc.)

Ne pas surcharger le log humain, prioriser le log debug structuré.

============================================
4. TESTS
============================================

Fichiers : tests/

4.1. Tests unitaires mémoire (si pas déjà faits) :
- test_memory_helpers_todo()
- test_memory_helpers_process()
- test_memory_helpers_protocol()

Exemples :
- sauvegarder un todo, vérifier qu’il est présent dans get_items("todo")
- sauvegarder un process, vérifier qu’il est listé
- idem pour protocol

4.2. Tests manuels via run_clara.py

Lancer :

    python3 run_clara.py

Scénarios à tester à la main (à documenter dans le journal) :

1) TODO :
   - "Ajoute un todo : appeler le fournisseur demain matin"
   - "Montre-moi mes todos"

2) PROCESS :
   - "Sauvegarde ce process : procédure pour vérifier un fournisseur : ..."
   - "Montre-moi la liste de mes process"

3) PROTOCOL :
   - "Sauvegarde ce protocole pour les mails fournisseurs : ..."
   - "Montre-moi mes protocoles"

Vérifier :
- pas d’erreur en terminal
- les entrées apparaissent bien dans memory.sqlite
- les réponses textuelles de Clara sont cohérentes avec les données réelles

============================================
5. JOURNAL CURSOR
============================================

Créer :

  journal/cursor_gpt/2025-12-05_phase3_5_memory_todo_process_protocol.md

Contenu attendu :
- Contexte : extension de la mémoire (notes → todo/process/protocol)
- Décisions : helpers ajoutés, intentions mémoire étendues, limites actuelles
- Fichiers modifiés : memory_core.py (si nécessaire), memory/helpers.py, orchestrator.py, tests
- Résultats : tests unitaires + tests manuels décrits
- Prochaines étapes : future phase contacts + intégration agents spécialisés / Autogen

============================================
6. COMMIT + PUSH
============================================

Une fois tout terminé et testé :

- Commit avec message EXACT :

    "Phase 3.5: extend memory to todo/process/protocol"

- Push sur main.

============================================
7. NE DOIS PAS FAIRE
============================================

- Ne pas commencer à gérer les contacts dans cette phase.
- Ne pas intégrer mail/calendar/whatsapp ici.
- Ne pas modifier la logique de base pour les notes (ne pas casser ce qui marche).
- Ne pas introduire de classe MemoryCore.
- Ne pas ajouter de logique d’autonomie “magique”.
- Ne pas changer la structure de la base sans raison critique.

############################################
# FIN – PHASE 3.5 MÉMOIRE TODO / PROCESS / PROTOCOL
############################################
