# Fix – Unification des chemins SQLite
Date: 2025-12-05

## Contexte

Après la Phase 2, un problème d'incohérence a été détecté : plusieurs fichiers référençaient des chemins SQLite différents :
- `memory/memory.sqlite` (nouveau standard Phase 2)
- `memory/clara_memory.db` (ancien nom Phase 1)

Cette incohérence pouvait créer plusieurs bases de données différentes et fragmenter la mémoire de Clara.

## Analyse

### Scan des références SQLite

**Fichiers utilisant `memory/memory.sqlite` ✅ :**
- `memory/memory_core.py` (6 occurrences) : toutes les fonctions par défaut
- `run_clara.py` : appel à `init_db()` sans paramètre
- Documentation et instructions Phase 2

**Fichiers utilisant `memory/clara_memory.db` ❌ :**
- `agents/orchestrator.py` ligne 24 : fallback dans `MemoryCore()`
- `config/settings.yaml` ligne 15 : paramètre `memory_db_path`
- `config/env.example` ligne 15 : variable `DATABASE_PATH`

**Fichiers non concernés :**
- `tests/test_memory_core.py` : utilise un fichier temporaire (correct)

### Diagnostic

Le problème était que :
1. `memory_core.py` créait/utilisait `memory.sqlite`
2. `orchestrator.py` essayait d'utiliser `clara_memory.db`
3. Deux bases SQLite distinctes étaient potentiellement créées

**Impact :** Fragmentation de la mémoire, perte de cohérence des données.

## Décision

**Fichier officiel retenu :** `memory/memory.sqlite`

**Raisons :**
- Nom plus explicite (module memory → fichier memory)
- Convention Phase 2 déjà implémentée dans `memory_core.py`
- Cohérent avec la structure du projet

**Actions à prendre :**
- Unifier tous les chemins vers `memory/memory.sqlite`
- Supprimer les références à `clara_memory.db`
- Mettre à jour la configuration et la documentation

## Changements effectués

### 1. `agents/orchestrator.py`
**Avant :**
```python
self.memory = MemoryCore(self.config.get('memory_db_path', 'memory/clara_memory.db'))
```

**Après :**
```python
self.memory = MemoryCore(self.config.get('memory_db_path', 'memory/memory.sqlite'))
```

### 2. `config/settings.yaml`
**Avant :**
```yaml
memory_db_path: memory/clara_memory.db
```

**Après :**
```yaml
memory_db_path: memory/memory.sqlite
```

### 3. `config/env.example`
**Avant :**
```
DATABASE_PATH=memory/clara_memory.db
```

**Après :**
```
DATABASE_PATH=memory/memory.sqlite
```

## Vérifications

✅ Tous les chemins SQLite unifié vers `memory/memory.sqlite`
✅ Aucune référence à `clara_memory.db` dans le code Python
✅ Configuration cohérente entre tous les fichiers
✅ `.gitignore` ignore déjà `*.db` et `*.sqlite`

## Test manuel

Clara démarre correctement et utilise le bon fichier :
```bash
python3 run_clara.py
```

Le fichier `memory/memory.sqlite` est créé automatiquement au premier lancement.

## Fichier obsolète

`clara_memory.db` (s'il existe) est maintenant obsolète et peut être supprimé localement.
Il n'est pas tracké par Git (ignoré par `.gitignore`).

## Prochaines étapes

Aucune action requise. La mémoire est maintenant unifiée et cohérente.

Phase 3 pourra utiliser cette base unique sans ambiguïté.

## Conclusion

**Fix SQLite Path ✅ TERMINÉ**

Clara utilise maintenant un seul et unique fichier SQLite : `memory/memory.sqlite`

Toutes les références sont cohérentes dans :
- Le code Python
- La configuration YAML
- Les exemples de variables d'environnement

🗄️ **Mémoire unifiée et cohérente !**




