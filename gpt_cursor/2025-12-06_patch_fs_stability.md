
# 2025-12-06_patch_fs_stability.md

## 🎯 Objectif

Rendre **FIABLE** tout ce qui touche au système de fichiers, avant de passer aux agents Autogen :

- Création / lecture / écriture de fichiers
- Création / liste de dossiers
- Déplacement / suppression de chemins
- Comportement 100 % prévisible et loggé

Clara doit **toujours** passer par `fs_driver` pour agir sur le disque, jamais en direct.

---

## 1. Drivers – fs_driver.py

### 1.1. API unique et standardisée

Vérifier / mettre en place les fonctions suivantes dans `drivers/fs_driver.py` :

```python
def ensure_dir(path: str) -> dict: ...
def list_dir(path: str) -> dict: ...
def path_exists(path: str) -> dict: ...
def read_file(path: str) -> dict: ...
def write_file(path: str, content: str, overwrite: bool = False) -> dict: ...
def move_path(src: str, dst: str) -> dict: ...
def delete_path(path: str) -> dict: ...
```

Format de retour **obligatoire** pour TOUTES :

```python
{
    "ok": bool,
    "error": str | None,
    "details": dict   # optionnel, mais toujours présent
}
```

Contraintes :

- `ensure_dir` crée tous les parents si nécessaire (`mkdir(parents=True, exist_ok=True)`).
- `write_file` :
  - si `overwrite=False` et le fichier existe → `ok=False`, `error="file_exists"`.
  - si `overwrite=True` → écrase proprement.
- `move_path` :
  - gère fichiers **et** dossiers.
  - si `src` n’existe pas → `ok=False`, `error="src_not_found"`.
- `delete_path` :
  - accepte fichiers **ou** dossiers (rmtree).
  - si n’existe pas → `ok=False`, `error="not_found"`.

**Important :**  
Aucune autre fonction dans le projet ne doit utiliser directement `os`, `pathlib`, `shutil` pour toucher au disque.  
Tout passe par `fs_driver`.

---

## 2. Orchestrator – agents/orchestrator.py

Objectif : éviter que Clara “croie” avoir fait quelque chose alors que le driver a échoué.

### 2.1. Chemin unique pour les actions FS

Dans la partie EXECUTION de l’orchestrator :

- Introduire un helper interne, par ex :

```python
from drivers import fs_driver

def _exec_fs_step(step: dict, session_id: str) -> dict:
    # step: {"op": "write_file", "params": {...}}
    # log avant/après + retour structuré
```

- Chaque fois que le PLAN contient une étape FS (`step["type"] == "fs"` ou équivalent actuel) :
  - Appeler `_exec_fs_step` (et donc `fs_driver.*`) **UNIQUEMENT**.
  - Ne jamais faire d’`open()`, `os.remove()`, etc.

### 2.2. Gestion stricte des erreurs

Dans la boucle qui exécute les steps :

- Si `_exec_fs_step` retourne `ok=False` :
  - Ajouter un bloc dans `execution_summary` du type :

    ```python
    {
      "type": "fs_error",
      "op": step["op"],
      "params": step.get("params", {}),
      "error": result["error"]
    }
    ```

  - **Arrêter** les steps suivants qui dépendent de celui-ci.
  - Marquer un flag global `had_fs_error = True`.

- Transmettre ce flag à la phase RESPOND (même fichier) pour que la réponse utilisateur soit **honnête** :

  - Si `had_fs_error` est True → Clara doit dire explicitement :
    - ce qu’elle a réussi à faire
    - ce qui a échoué
    - sur quel chemin
    - avec quel type d’erreur (fichier inexistant, etc.)

Pas de “tout va bien” si `had_fs_error=True`.

---

## 3. Helpers & logs – helpers.py / logs

### 3.1. Wrapper de logging FS

Dans `helpers.py`, ajouter un wrapper :

```python
def log_fs_action(logger, session_id: str, step: dict, result: dict) -> None:
    # Ajoute dans le debug log un enregistrement structuré de l'action FS.
    ...
```

À appeler depuis `_exec_fs_step` :

- Avant l’appel driver → log `{"event": "fs_start", ...}`
- Après l’appel driver → log `{"event": "fs_end", "ok": ..., "error": ...}`

Le logger utilisé doit être le même que pour les autres debug logs de session (fichier `session_*.json` / debug).

### 3.2. Ce que JE veux voir dans les logs

Pour chaque action FS, dans les logs de debug :

```json
{
  "phase": "EXEC",
  "subsystem": "fs",
  "session_id": "...",
  "step": {
    "op": "write_file",
    "params": {"path": "...", "overwrite": true}
  },
  "result": {
    "ok": true,
    "error": null,
    "details": {...}
  }
}
```

---

## 4. Nettoyage & interdictions

1. **Recherche globale** dans le repo :
   - Interdire toute utilisation directe de `os`, `open()`, `shutil`, `pathlib` pour des actions FS OUTSIDE `fs_driver.py`.
   - Si trouvé :
     - soit supprimer,
     - soit rerouter vers `fs_driver`.

2. Ajouter un commentaire clair en haut de `fs_driver.py` :

```python
# RÈGLE : toute action sur le système de fichiers DOIT passer par ce module.
# Ne jamais toucher au disque depuis l'orchestrator, les agents ou les UI.
```

---

## 5. Tests à faire (obligatoires)

Créer/adapter des tests (ou au moins un script manuel) pour vérifier, en conditions réelles :

1. **Création fichier**
   - “Crée un fichier test dans un nouveau dossier X et écris du texte dedans.”
   - Vérifier sur disque et dans les logs.

2. **Déplacement**
   - “Déplace ce fichier dans Y.”
   - Vérifier que :
     - le fichier n’est plus dans X,
     - est bien dans Y,
     - les logs montrent un `move_path` `ok=True`.

3. **Suppression**
   - “Supprime le fichier que tu viens de créer.”
   - Vérifier que :
     - le fichier n’existe plus,
     - les logs montrent un `delete_path` `ok=True`.

4. **Erreur contrôlée**
   - Demander à Clara de déplacer un fichier inexistant.
   - Attendu :
     - `ok=False`, `error="src_not_found"` dans les logs.
     - Réponse utilisateur claire : elle dit qu’elle n’a pas trouvé le fichier, et qu’elle n’a rien fait d’autre.

---

## 6. Discipline de test pour Cursor

À la fin du patch :

- Lancer **Clara en vrai** (`python run_clara.py`).
- Faire au minimum les 4 tests ci-dessus.
- Documenter le résultat dans un fichier :

`journal/cursor_gpt/2025-12-06_fs_driver_stability_tests.md`

Avec :

- Contexte
- Commandes envoyées à Clara
- Résultat observé (OK / KO)
- Si KO → explication et correctif appliqué.

Merci de ne rien livrer tant que les 4 scénarios ne sont pas **100 % verts**.
