# Archive des interventions Cursor

Ce dossier contient l'historique de toutes les interventions de Cursor sur le projet Clara.

## Structure

```
cursor_gpt/
├── instructions/     # Instructions originales de l'utilisateur (archivées)
└── reports/          # Rapports d'exécution de Cursor
```

## Règles

1. **Instructions** (`instructions/`) :
   - Fichiers d'instructions de l'utilisateur archivés tels quels
   - Ne jamais modifier ces fichiers
   - Conservation de l'historique des demandes

2. **Rapports** (`reports/`) :
   - Un rapport par intervention de Cursor
   - Format : `YYYY-MM-DD_nom_mission.md`
   - Contenu : Contexte, Instructions reçues, Actions effectuées, Changements, Prochaines étapes

## Workflow

1. Utilisateur place instructions dans `gpt_cursor/`
2. Cursor lit et exécute
3. Cursor archive les instructions dans `instructions/`
4. Cursor écrit son rapport dans `reports/`

→ Séparation claire entre ce qui est demandé et ce qui est fait.

