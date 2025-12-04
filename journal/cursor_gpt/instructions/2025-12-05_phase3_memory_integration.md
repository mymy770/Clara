############################################
# PHASE 3 – CONNEXION CLARA ↔ MÉMOIRE
# Instructions pour Cursor – À exécuter EXACTEMENT
# Fichier recommandé : gpt_cursor/2025-12-05_phase3_memory_integration.md
############################################

🎯 OBJECTIF GLOBAL
Donner à Clara une vraie mémoire de travail simple et stable, basée sur SQLite,
SANS logique magique, SANS cas particuliers, et SANS casser l’architecture actuelle.

En fin de PHASE 3, Clara doit pouvoir :
  - créer / lire / chercher / supprimer des éléments de mémoire
  - au moins pour les types : note, contact, process, protocol, todo
  - via une API propre, réutilisable par les futurs agents.

On NE fait PAS encore d’autonomie avancée (détection automatique de ce qui doit
être mémorisé). On prépare une base saine + quelques usages explicites.

============================================
1. RAPPEL – CONTRAINTES IMPORTANTES
============================================

1) Ne PAS introduire de classe MemoryCore si elle n’existe pas déjà.
   On reste sur une API fonctionnelle dans memory_core.py.

2) Ne PAS modifier la structure de la table `memory` dans schema.sql pour cette phase,
   sauf bug évident. On utilise ce qui existe déjà.

3) Ne PAS réintroduire de dépendance circulaire entre orchestrator et memory_core.

4) Ne PAS mélanger logique “mémoire” et logique “mail / agenda / whatsapp”.
   Ici on ne touche qu’à la mémoire générique.

5) Ne PAS ajouter de logique métier lourde dans memory_core.py.
   C’est une couche d’accès aux données, pas un cerveau.

============================================
2. MEMORY_CORE – API MÉMOIRE GÉNÉRIQUE
============================================

Fichier : memory/memory_core.py

2.1. Vérifier / stabiliser les fonctions suivantes (ou les créer si manquantes) :

  - init_db()
  - save_item(type: str, content: str, tags: list[str] | None = None) -> int
  - update_item(item_id: int, content: str | None = None,
                tags: list[str] | None = None) -> None
  - get_items(type: str | None = None,
              limit: int = 50,
              order: str = "desc") -> list[dict]
  - search_items(type: str | None,
                 query: str,
                 limit: int = 50) -> list[dict]
  - delete_item(item_id: int) -> None

Règles :
  - Utiliser le chemin unique : db_path = "memory/memory.sqlite"
  - Toujours retourner des dicts simples pour les items, par ex :
        {
          "id": int,
          "type": str,
          "content": str,
          "tags": list[str] | None,
          "created_at": str,
          "updated_at": str
        }
  - `tags` est stocké en base sous forme de texte (JSON ou CSV), mais renvoyé
    au code Python sous forme de liste (ou None).

2.2. Ajouter une petite couche helper OPTIONNELLE (facultatif mais utile) :

  Dans le même fichier ou dans un petit module séparé memory/helpers.py, ajouter
  des fonctions simples de confort, par ex :

    - save_note(content: str, tags: list[str] | None = None) -> int
    - save_process(content: str, tags: list[str] | None = None) -> int
    - save_protocol(content: str, tags: list[str] | None = None) -> int
    - save_todo(content: str, tags: list[str] | None = None) -> int

  Ces helpers appellent simplement save_item(type="note" / "process" / "protocol" / "todo", ...).

  ⚠ Si tu crées un helper module, respecter l’architecture :
    - memory/memory_core.py = accès DB
    - memory/helpers.py     = fonctions typées par type

============================================
3. ORCHESTRATOR – UTILISATION BASIQUE DE LA MÉMOIRE
============================================

Fichier : agents/orchestrator.py

Objectif Phase 3 :
  - Donner à Clara un accès basique à la mémoire, de manière EXPLICITE,
    via quelques commandes “humaines” simples,
    SANS mettre de logique magique difficile à contrôler.

3.1. Importer la mémoire

  Ajouter en haut du fichier (adapter au chemin réel) :

    from memory.memory_core import save_item, get_items, search_items, delete_item

  ou, si helpers créés, éventuellement :

    from memory.helpers import save_note, save_process, save_protocol, save_todo
    from memory.memory_core import get_items, search_items, delete_item

3.2. Pattern pour les commandes mémoire (Phase 3 = simple, explicite)

  On veut que Clara soit capable au minimum de traiter des demandes du type :

    - "Sauvegarde ceci en note : …"
    - "Montre-moi toutes mes notes"
    - "Cherche dans mes notes les occurrences de …"
    - "Supprime cette note avec l’id X"

  Pour cette phase, on utilise une approche simple :

    - L’orchestrateur interprète la demande utilisateur (via le LLM)
      ET, si le LLM retourne une intention claire "memory_*",
      on appelle la fonction de mémoire correspondante.

  Concrètement :

  1) Dans la construction du prompt LLM (SYSTEM ou instructions), ajouter une section :
     - décrivant les capacités mémoire disponibles :
         - memory_save_note
         - memory_list_notes
         - memory_search_notes
         - memory_delete_item
     - demandant au modèle de retourner une petite structure JSON d’intention
       EN PLUS du texte de réponse humaine.

     Ex : dans la réponse, le modèle peut renvoyer un bloc délimité du type :

       ```json
       {"memory_action": "save_note", "content": "...", "tags": ["..."]}
       ```

  2) Côté code orchestrator :
     - après avoir reçu la réponse brute du LLM, parser ce bloc JSON d’intention
       (si présent).
     - SI `memory_action` est présent :
         - appeler la fonction adéquate (save_item / get_items / search_items / delete_item).
         - logguer l’action dans logs/sessions/… (partie debug).
     - NE PAS planter si le JSON n’est pas présent ou invalide : dans ce cas,
       on répond juste le texte au user.

  ⚠ IMPORTANT :
    - Ne pas multiplier les actions ni les cas particuliers.
    - Phase 3 = seulement quelques actions basiques sur type="note"
      (et éventuellement "todo") :
         - save_note
         - list_notes
         - search_notes
         - delete_item

    - Contacts / process / protocol peuvent être préparés côté API mémoire,
      mais pas forcément exposés tout de suite à l’orchestrateur si cela complique.
      L’objectif est un premier cycle mémoire stable, pas tout faire d’un coup.

3.3. Logging

  Lorsque l’orchestrateur exécute une action mémoire, logguer dans les logs de session :
    - type d’action ("memory.save_note", "memory.list_notes", …)
    - paramètres principaux (sans secrets)
    - résultat simplifié (nb éléments, id créé, etc.)

  Ne pas surcharger le log humain, mais enrichir surtout le log debug JSON.

============================================
4. TESTS DE PHASE 3
============================================

Créer ou compléter des tests dans le dossier : tests/

4.1. Tests unitaires mémoire (si pas déjà faits) :
  - test_memory_core_save_and_get()
  - test_memory_core_search()
  - test_memory_core_delete()

4.2. Tests manuels orchestrator (décrits dans journal) :
  Lancer run_clara.py puis tester à la main :
    1) "Sauvegarde ceci en note : Clara Phase 3 test"
    2) "Montre-moi toutes mes notes"
    3) "Cherche dans mes notes le mot 'Phase 3'"
    4) "Supprime la note avec l'id X" (à partir d’un id retourné)

  Vérifier :
    - pas d’erreur en terminal
    - la base memory/memory.sqlite se remplit bien
    - la réponse de Clara reste naturelle

============================================
5. JOURNAL CURSOR
============================================

Créer un fichier de journal :

  journal/cursor_gpt/2025-12-05_phase3_memory_integration.md

Contenu attendu :
  - Contexte : passage Phase 2 → Phase 3, mémoire déjà initialisée mais non utilisée.
  - Décisions : API mémoire générique, actions exposées à l’orchestrateur, limites de la phase.
  - Fichiers modifiés : liste précise (memory_core.py, orchestrator.py, tests, prompts éventuels).
  - Résultats : tests passés, commandes vérifiées.
  - Prochaines étapes : extension vers autres types (contacts, process, protocol, todo) et
    future intégration agents spécialisés + Autogen.

============================================
6. COMMIT + PUSH
============================================

Une fois terminé :

  - Vérifier que `python3 run_clara.py` fonctionne.
  - Vérifier au moins un round complet de :
       - save_note
       - list_notes
       - search_notes
    via le chat.

  - Commit avec le message EXACT :
       "Phase 3: connect orchestrator to memory core (notes basics)"

  - Push sur main.

============================================
7. NE DOIS PAS FAIRE
============================================

  - Ne pas implémenter une logique mémoire complexe (détection automatique
    de tout ce qui doit être enregistré) dans cette phase.
  - Ne pas modifier le schéma SQL sans raison critique.
  - Ne pas toucher aux drivers mail / calendar / whatsapp dans cette phase.
  - Ne pas introduire Autogen ou multi-agents ici.
  - Ne pas mélanger la mémoire avec des fonctionnalités réseau ou filesystem.

############################################
# FIN – PHASE 3 CONNEXION CLARA ↔ MÉMOIRE
############################################
