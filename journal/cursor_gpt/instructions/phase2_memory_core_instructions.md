############################################
# PHASE 2 – MEMORY CORE (CLARA PROJECT)
# Instructions pour Cursor – À exécuter EXACTEMENT
############################################

## CONTEXTE
Tu dois créer le moteur de mémoire interne de Clara.
Pas d'intelligence. Pas d'interprétation. Juste stockage brut.
Clara utilisera cette mémoire plus tard, mais pour l’instant c’est juste une API propre.

############################################
# 1. STRUCTURE BDD SQLITE
############################################

Créer un fichier SQLite : memory/memory.sqlite
Si le fichier n'existe pas → le créer automatiquement au premier accès.

Dans memory/schema.sql, définir la structure suivante exactement :

CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Types de base visés (ne PAS les hardcoder dans le schéma) :
- contact
- task
- todo
- preference
- process
- protocol
- note
- project
- fact

############################################
# 2. MODULE memory_core.py
############################################

Créer / compléter memory/memory_core.py avec une API claire, sans logique métier.

Implémenter au minimum les fonctions suivantes :

1) init_db(
       db_path: str = "memory/memory.sqlite",
       schema_path: str = "memory/schema.sql"
   ) -> None
   - Crée le dossier memory si nécessaire.
   - Crée le fichier SQLite s’il n’existe pas.
   - Applique le schema.sql si la table n’existe pas.
   - À appeler au démarrage de Clara (dans run_clara.py).

2) save_item(
       type: str,
       content: str,
       tags: list[str] | None = None,
       db_path: str = "memory/memory.sqlite"
   ) -> int
   - Insère un nouvel item dans memory.
   - Sérialise tags en JSON (ou NULL si None).
   - Retourne l’id créé (int).

3) update_item(
       item_id: int,
       content: str | None = None,
       tags: list[str] | None = None,
       db_path: str = "memory/memory.sqlite"
   ) -> None
   - Met à jour content et/ou tags si fournis.
   - Met à jour updated_at à CURRENT_TIMESTAMP.
   - Ne fait rien si aucun champ n’est fourni.

4) get_items(
       type: str | None = None,
       limit: int | None = None,
       db_path: str = "memory/memory.sqlite"
   ) -> list[dict]
   - Retourne une liste de dicts :
     {id, type, content, tags (list[str] ou []), created_at, updated_at}.
   - Si type est fourni → filtrer sur ce type.
   - Si limit est fourni → limiter le nombre de lignes
     (ORDER BY created_at DESC).

5) search_items(
       query: str,
       type: str | None = None,
       db_path: str = "memory/memory.sqlite"
   ) -> list[dict]
   - Recherche simple via LIKE '%query%' sur content.
   - Si type est fourni → filtrer aussi sur type.
   - Même format de retour que get_items().

6) delete_item(
       item_id: int,
       db_path: str = "memory/memory.sqlite"
   ) -> None
   - Supprime la ligne correspondant à id.

CONTRAINTES TECHNIQUES :
- Utiliser sqlite3 (standard lib).
- Utiliser json.dumps / json.loads pour tags.
- Toujours utiliser des context managers (with sqlite3.connect(...) as conn).
- Activer une row_factory pour récupérer des colonnes nommées,
  puis convertir en dict.
- AUCUNE logique métier : pas de règles sur les types, pas de mapping spécial,
  pas d’IA, pas de LLM ici.
- Ce module doit être purement technique et réutilisable.

############################################
# 3. INTÉGRATION DANS run_clara.py
############################################

Dans run_clara.py :
- Importer init_db depuis memory.memory_core.
- Appeler init_db() au démarrage, AVANT la boucle d’input utilisateur.
- Ne PAS encore appeler save_item / get_items / search_items / delete_item
  dans le flux de conversation.
  (Phase 2 = infrastructure mémoire uniquement.)

############################################
# 4. JOURNALISATION CURSOR
############################################

Créer un fichier de journal dans :
journal/cursor_gpt/2025-12-04_phase2_memory_core.md

Contenu attendu (structure minimale) :
- Contexte : pourquoi cette phase, ce qui existait déjà.
- Décisions : choix du schéma, choix de l’API Python.
- Changements effectués : fichiers créés/modifiés.
- Prochaines étapes : comment la mémoire sera utilisée en Phase 3.

############################################
# 5. NE DOIS PAS FAIRE
############################################

Tu NE dois PAS :
- Modifier orchestrator.py
- Modifier drivers/*
- Modifier agents/*
- Ajouter de la logique d’agents autour de la mémoire
- Commencer à interpréter les types (contact, todo, etc.) côté memory_core

Tout ça viendra en Phase 3, quand on branchera les agents
et la logique métier sur cette API mémoire stable.

############################################
# FIN – PHASE 2 MEMORY CORE
############################################