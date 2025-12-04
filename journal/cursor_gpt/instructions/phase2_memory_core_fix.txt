############################################
# FIX – SQLITE FILE NAME (memory.sqlite vs clara_memory.db)
# Instructions pour Cursor – À exécuter EXACTEMENT
############################################

🎯 OBJECTIF
Assurer que Clara utilise UN SEUL fichier SQLite cohérent,
et que tous les chemins pointent vers le même fichier.

Le fichier officiel doit être :
    memory/memory.sqlite

############################################
# 1. SCAN DES CHEMINS SQLITE
############################################

1) Scanner tout le projet Clara et lister tous les endroits où un fichier SQLite est mentionné :
   - "memory/memory.sqlite"
   - "clara_memory.db"
   - tout autre chemin .db ou .sqlite

   Vérifier en particulier :
   - memory/memory_core.py
   - run_clara.py
   - tout autre module qui pourrait référencer une base SQLite.

2) Faire un court résumé dans un commentaire dans le journal (voir §4) :
   - où chaque chemin a été trouvé
   - quel chemin est réellement utilisé à l’exécution

############################################
# 2. FICHIER OFFICIEL À GARDER
############################################

Le fichier de référence DOIT être :
    memory/memory.sqlite

Actions à faire :

1) Vérifier que memory_core.py utilise bien par défaut :
   db_path = "memory/memory.sqlite"

2) Vérifier que run_clara.py (ou tout autre fichier) ne référence PAS un autre nom
   (par exemple "clara_memory.db").

3) Si un nom différent est utilisé quelque part :
   - le remplacer proprement par "memory/memory.sqlite"
   - s’assurer que les imports et appels restent cohérents.

############################################
# 3. GESTION DE clara_memory.db
############################################

Si un fichier clara_memory.db existe encore dans le repo local :

1) Vérifier s’il est encore référencé dans le code :
   - S’il N’EST PAS référencé → le considérer comme ancien / obsolète.

2) Ne PAS le committer dans Git :
   - S’assurer que .gitignore ignore bien tous les fichiers .db dans memory/
     ou explicitement clara_memory.db si nécessaire.

3) Tu peux supprimer clara_memory.db localement s’il est clairement obsolète
   (mais ne PAS committer sa suppression si le fichier n’est pas tracké par Git).

############################################
# 4. JOURNALISATION CURSOR
############################################

Créer un fichier de journal :

    journal/cursor_gpt/2025-12-05_fix_sqlite_path.md

Contenu attendu (structure minimale) :
- Contexte : doublon de fichiers SQLite (memory.sqlite vs clara_memory.db)
- Analyse : où chaque chemin était utilisé
- Décision : fichier officiel retenu (memory/memory.sqlite)
- Changements : fichiers modifiés, chemins unifiés
- Prochaines étapes : rien, ou note pour Phase 3 si besoin

############################################
# 5. COMMIT + PUSH
############################################

Une fois les corrections effectuées :

1) Vérifier que :
   - Clara démarre sans erreur
   - La base SQLite est bien créée / utilisée dans memory/memory.sqlite

2) Faire un commit avec le message EXACT :
   Fix: unified SQLite paths and cleaned obsolete DB reference

3) Push sur la branche main.

############################################
# 6. NE DOIS PAS FAIRE
############################################

Tu NE dois PAS :
- Modifier orchestrator.py
- Modifier les agents/*
- Modifier la structure de la table memory dans schema.sql
- Ajouter de la logique métier autour de la mémoire

############################################
# FIN – FIX SQLITE PATH
############################################