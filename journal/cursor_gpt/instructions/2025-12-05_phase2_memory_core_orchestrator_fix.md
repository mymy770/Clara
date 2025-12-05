############################################
# PHASE 2 – FIX ORCHESTRATOR & STABILISER memory.sqlite
# Instructions pour Cursor – À exécuter EXACTEMENT
############################################

🎯 OBJECTIF
1) Supprimer toute dépendance à une classe MemoryCore qui n’existe pas.
2) S’assurer que la mémoire SQLite officielle est bien : memory/memory.sqlite
3) Laisser Clara démarrer proprement (Phase 2) avec mémoire initialisée, mais pas encore utilisée par l’orchestrateur.

############################################
# 1. ORCHESTRATOR : SUPPRIMER L’ANCIENNE INTÉGRATION MÉMOIRE
############################################

Fichier : agents/orchestrator.py

1) Supprimer l’import suivant s’il existe :

    from memory.memory_core import MemoryCore

2) Supprimer ou commenter toute initialisation de MemoryCore, par exemple :

    self.memory = MemoryCore(self.config.get('memory_db_path', 'memory/memory.sqlite'))

3) Supprimer ou commenter provisoirement toutes les méthodes qui utilisent self.memory,
   par exemple (les noms exacts peuvent varier) :

    - save_interaction(...)
    - load_session_context(...)
    - tout appel à self.memory.save_...(…)
    - tout appel à self.memory.load_...(…)

BUT : en Phase 2, l’orchestrateur NE DOIT PAS encore utiliser la mémoire.
Il doit juste :
    - recevoir le message utilisateur
    - appeler le LLM
    - renvoyer la réponse

Aucune logique mémoire dans agents/orchestrator.py pour l’instant.

############################################
# 2. MEMORY_CORE : CONFIRMER LE FICHIER OFFICIEL
############################################

Fichier : memory/memory_core.py

1) Vérifier qu’il existe un chemin par défaut unique pour la BDD, par exemple :

    DB_PATH_DEFAULT = "memory/memory.sqlite"

ou à défaut que toutes les fonctions utilisent :

    db_path: str = "memory/memory.sqlite"

2) Vérifier que AUCUNE fonction ne référence clara_memory.db ou un autre nom.

3) Vérifier que init_db() :
    - crée le dossier memory/ si nécessaire
    - lit memory/schema.sql
    - applique le schéma sur memory/memory.sqlite

Ne pas modifier la structure de la table ni la logique déjà en place,
juste confirmer que tout pointe vers memory/memory.sqlite.

############################################
# 3. run_clara.py : INITIALISATION MÉMOIRE AU DÉMARRAGE
############################################

Fichier : run_clara.py

1) Vérifier qu’on importe bien init_db :

    from memory.memory_core import init_db

2) Vérifier qu’on appelle init_db() AVANT de démarrer la boucle de chat, par exemple :

    def main():
        init_db()
        # puis initialisation de l’orchestrateur et de la boucle de conversation

Si ce n’est pas le cas, l’ajouter.
Ne pas ajouter d’autres appels à save_item / get_items à ce stade.

############################################
# 4. TEST DE DÉMARRAGE
############################################

Après modifications :

1) Lancer localement (terminal) :

    python3 run_clara.py

2) Vérifier :
    - Aucune erreur d’import liée à MemoryCore
    - Aucune exception liée à memory_core
    - Le fichier memory/memory.sqlite est bien créé si absent

3) Faire un échange simple dans le chat (ex : “test”) pour vérifier que Clara répond.

############################################
# 5. JOURNALISATION CURSOR
############################################

Créer :

    journal/cursor_gpt/2025-12-05_orchestrator_memory_alignment.md

Contenu attendu (court, structuré) :
- Contexte : erreur ImportError sur MemoryCore, phase 2 mémoire déjà fonctionnelle
- Décisions : 
    - suppression de l’ancienne intégration MemoryCore dans l’orchestrateur
    - confirmation de memory/memory.sqlite comme fichier officiel
    - init_db() appelé au démarrage uniquement
- Fichiers modifiés : liste précise
- Prochaines étapes : 
    - Phase 3 : connecter l’orchestrateur à memory_core via une API claire (save_item, get_items, etc.)

############################################
# 6. COMMIT + PUSH
############################################

1) Commit avec message EXACT :

    Fix: align orchestrator with new memory core and stabilize SQLite path

2) Push sur la branche main.

############################################
# 7. NE DOIS PAS FAIRE
############################################

- NE PAS réintroduire une classe MemoryCore.
- NE PAS ajouter de logique métier dans memory_core.py.
- NE PAS commencer à utiliser la mémoire dans les agents (ce sera pour la Phase 3).
- NE PAS modifier orchestrator pour ajouter des comportements “intelligents” supplémentaires.

############################################
# FIN – PHASE 2 ORCHESTRATOR + SQLITE STABILISÉ
############################################