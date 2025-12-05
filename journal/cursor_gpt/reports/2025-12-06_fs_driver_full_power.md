# 2025-12-06 – FS Driver Full Power

## Contexte

Implémentation d'un driver filesystem complet pour Clara, permettant à l'orchestrateur (et futurs agents Autogen) de manipuler des fichiers et dossiers de manière sécurisée.

## Changements effectués

### 1. Driver Filesystem (`drivers/fs_driver.py`)

Création d'un driver complet avec :
- **Lecture/Écriture** : `read_text`, `write_text`, `append_text`, `read_bytes`, `write_bytes`
- **Navigation** : `list_dir`, `make_dir`, `move_path`, `delete_path`
- **Utilitaires** : `stat_path`, `search_text` (recherche récursive avec filtres)

**Sécurité** : Toutes les opérations sont confinées sous `root_path`, empêchant toute sortie du workspace (pas de `../` qui remonte).

### 2. Helpers (`agents/helpers.py`)

Création d'un module helpers avec :
- `set_fs_driver()` : Configuration du driver
- `execute_fs_action()` : Point d'entrée générique pour toutes les actions filesystem

### 3. Intégration Orchestrateur

**Modifications dans `agents/orchestrator.py`** :
- Ajout du paramètre `fs_driver` dans `__init__()`
- Extension du prompt système avec section FILESYSTEM
- Nouvelle méthode `_process_filesystem_action()` pour parser et exécuter les intentions filesystem
- Gestion des intentions JSON avec `intent: "filesystem"`

**Actions supportées** :
- `read_text`, `write_text`, `append_text`
- `list_dir`, `make_dir`, `move_path`, `delete_path`
- `stat_path`, `search_text`

### 4. Initialisation

**Modifications dans `run_clara.py`** :
- Initialisation du `FSDriver` avec `workspace_root`
- Passage du driver à l'orchestrateur

**Modifications dans `api_server.py`** :
- Initialisation du `FSDriver` au démarrage
- Configuration via `set_fs_driver()`
- Passage du driver à l'orchestrateur global

### 5. Tests (`tests/test_fs_driver.py`)

Création de tests unitaires complets :
- Écriture/lecture texte et bytes
- Ajout de texte
- Listage de dossiers
- Création de dossiers
- Déplacement de fichiers
- Suppression (fichiers et dossiers)
- Récupération d'infos (stat)
- Recherche de texte
- Filtrage par extensions
- Confinement de sécurité (pas de sortie du root)

## Fichiers touchés

- `drivers/fs_driver.py` (créé)
- `agents/helpers.py` (créé)
- `agents/orchestrator.py` (modifié)
- `run_clara.py` (modifié)
- `api_server.py` (modifié)
- `tests/test_fs_driver.py` (créé)

## Tests réalisés

Tous les tests unitaires passent :
- ✅ Écriture/lecture texte et bytes
- ✅ Ajout de texte
- ✅ Navigation (list_dir, make_dir)
- ✅ Déplacement et suppression
- ✅ Recherche de texte
- ✅ Sécurité (confinement root)

## Limites / TODO

- **PDF** : Non géré pour l'instant (extensible plus tard)
- **Permissions** : Le driver assume les permissions système (pas de gestion fine)
- **Performance** : `search_text` peut être lent sur de gros dossiers (limité à 100 fichiers par défaut)

## Exemple d'utilisation

Clara peut maintenant :
- Lire des fichiers : "Lis le fichier journal/dev_notes/..."
- Créer des rapports : "Crée un rapport dans reports/..."
- Rechercher : "Cherche 'Clara' dans les fichiers"
- Organiser : "Déplace ce fichier dans archive/"

Le LLM génère automatiquement l'intention JSON appropriée.

