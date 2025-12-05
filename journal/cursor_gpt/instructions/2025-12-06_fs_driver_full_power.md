# 2025-12-06_fs_driver_full_power.md
## Contexte
Projet : **Clara**  
Objectif : Ajouter un **driver filesystem complet** + intégration orchestrator, pour que Clara (et plus tard les agents Autogen) puissent :
- lire / écrire / créer / déplacer / supprimer des fichiers et dossiers,
- lister / explorer le workspace,
- rechercher du texte,
- préparer des exports de rapports (txt / md, extensible vers PDF).

Tu travailles dans le repo Clara déjà initialisé.

---

## 1. Nouveau driver : `drivers/fs_driver.py`

### 1.1. Créer / remplacer le fichier

Créer (ou écraser s’il existe) : `drivers/fs_driver.py` avec une implémentation propre, sans dépendances exotiques :

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import shutil
import logging

logger = logging.getLogger(__name__)


@dataclass
class FSItem:
    path: str           # chemin relatif au root
    is_dir: bool
    size: Optional[int] = None
    modified_ts: Optional[float] = None


class FSDriver:
    """Driver filesystem sûr et générique pour Clara.

    - Toutes les opérations sont confinées sous root_path.
    - Ne jamais sortir du root (pas de .. qui remonte).
    - Pensé pour être utilisé par l'orchestrateur et les futurs agents.
    """

    def __init__(self, root_path: Path) -> None:
        self.root_path = root_path.resolve()
        self.root_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"FSDriver root set to: {self.root_path}")

    # ---------- utils internes ----------

    def _resolve(self, relative_path: str) -> Path:
        if not relative_path:
            return self.root_path
        p = (self.root_path / relative_path).resolve()
        # confinement root
        if self.root_path not in p.parents and p != self.root_path:
            raise ValueError(f"Path escapes root: {relative_path}")
        return p

    # ---------- lecture / écriture ----------

    def read_text(self, relative_path: str, encoding: str = "utf-8") -> str:
        path = self._resolve(relative_path)
        logger.debug(f"FSDriver.read_text: {path}")
        return path.read_text(encoding=encoding)

    def read_bytes(self, relative_path: str) -> bytes:
        path = self._resolve(relative_path)
        logger.debug(f"FSDriver.read_bytes: {path}")
        return path.read_bytes()

    def write_text(
        self,
        relative_path: str,
        content: str,
        encoding: str = "utf-8",
        overwrite: bool = True,
    ) -> None:
        path = self._resolve(relative_path)
        logger.debug(f"FSDriver.write_text: {path} overwrite={overwrite}")
        path.parent.mkdir(parents=True, exist_ok=True)
        if not overwrite and path.exists():
            raise FileExistsError(f"File already exists: {relative_path}")
        path.write_text(content, encoding=encoding)

    def append_text(self, relative_path: str, content: str, encoding: str = "utf-8") -> None:
        path = self._resolve(relative_path)
        logger.debug(f"FSDriver.append_text: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding=encoding) as f:
            f.write(content)

    def write_bytes(
        self,
        relative_path: str,
        content: bytes,
        overwrite: bool = True,
    ) -> None:
        path = self._resolve(relative_path)
        logger.debug(f"FSDriver.write_bytes: {path} overwrite={overwrite}")
        path.parent.mkdir(parents=True, exist_ok=True)
        if not overwrite and path.exists():
            raise FileExistsError(f"File already exists: {relative_path}")
        path.write_bytes(content)

    # ---------- dossiers / navigation ----------

    def list_dir(self, relative_path: str = "") -> List[FSItem]:
        base = self._resolve(relative_path)
        logger.debug(f"FSDriver.list_dir: {base}")
        if not base.exists():
            return []
        items: List[FSItem] = []
        for child in base.iterdir():
            stat = child.stat()
            items.append(
                FSItem(
                    path=str(child.relative_to(self.root_path)),
                    is_dir=child.is_dir(),
                    size=None if child.is_dir() else stat.st_size,
                    modified_ts=stat.st_mtime,
                )
            )
        return items

    def make_dir(self, relative_path: str, exist_ok: bool = True) -> None:
        path = self._resolve(relative_path)
        logger.debug(f"FSDriver.make_dir: {path}")
        path.mkdir(parents=True, exist_ok=exist_ok)

    def move_path(self, src_relative: str, dst_relative: str, overwrite: bool = False) -> None:
        src = self._resolve(src_relative)
        dst = self._resolve(dst_relative)
        logger.debug(f"FSDriver.move_path: {src} -> {dst} overwrite={overwrite}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not overwrite:
            raise FileExistsError(f"Destination exists: {dst_relative}")
        shutil.move(str(src), str(dst))

    def delete_path(self, relative_path: str) -> None:
        path = self._resolve(relative_path)
        logger.debug(f"FSDriver.delete_path: {path}")
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()

    # ---------- utilitaires avancés ----------

    def stat_path(self, relative_path: str) -> Dict[str, Any]:
        path = self._resolve(relative_path)
        logger.debug(f"FSDriver.stat_path: {path}")
        if not path.exists():
            return {"exists": False}
        st = path.stat()
        return {
            "exists": True,
            "is_dir": path.is_dir(),
            "size": None if path.is_dir() else st.st_size,
            "modified_ts": st.st_mtime,
            "absolute_path": str(path),
            "relative_path": str(path.relative_to(self.root_path)),
        }

    def search_text(
        self,
        query: str,
        start_relative: str = "",
        max_files: int = 100,
        extensions: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Recherche simple de texte dans des fichiers.

        - Parcourt récursivement à partir de start_relative.
        - Filtre optionnel par extensions (ex: [".txt", ".md"]).
        - Retourne une liste d'occurrences (fichier + extrait).
        """
        base = self._resolve(start_relative)
        logger.debug(f"FSDriver.search_text: query={query!r} base={base}")
        if not base.exists():
            return []

        results: List[Dict[str, Any]] = []
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if extensions is not None and path.suffix not in extensions:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if query.lower() in text.lower():
                rel = str(path.relative_to(self.root_path))
                snippet = self._extract_snippet(text, query)
                results.append({"path": rel, "snippet": snippet})
                if len(results) >= max_files:
                    break
        return results

    @staticmethod
    def _extract_snippet(text: str, query: str, radius: int = 60) -> str:
        idx = text.lower().find(query.lower())
        if idx == -1:
            return text[:radius * 2]
        start = max(0, idx - radius)
        end = min(len(text), idx + len(query) + radius)
        snippet = text[start:end].replace("\n", " ")
        return snippet
```

**Important :** ne pas ajouter de logique métier Clara ici, uniquement des primitives FS.

---

## 2. Intégration avec l’orchestrateur

Objectif : permettre à Clara de demander proprement des opérations FS via une intention JSON.

### 2.1. Initialisation du FSDriver

Dans `run_clara.py` (ou le module qui initialise les drivers), ajouter quelque chose de ce type :

```python
from pathlib import Path
from drivers.fs_driver import FSDriver

# ...
workspace_root = Path(__file__).resolve().parent  # racine du projet Clara
fs_driver = FSDriver(root_path=workspace_root)
```

⚠️ Si un autre fichier centralise déjà les drivers, adapter en conséquence.  
Le but : **avoir une instance unique `fs_driver` que l’orchestrateur peut utiliser.**


### 2.2. Ajouter un helper FS dans `agents/helpers.py`

Dans `agents/helpers.py`, ajouter un bloc pour exposer le FS à l’orchestrateur :

```python
from typing import Any, Dict
from drivers.fs_driver import FSDriver

# fs_driver doit être importé ou injecté – adapter selon l'architecture actuelle
fs_driver: FSDriver  # à câbler proprement là où les helpers sont initialisés


def execute_fs_action(action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Point d'entrée générique pour les actions filesystem.

    action: nom d'action (read_text, write_text, list_dir, etc.)
    params: dict d'arguments attendu par FSDriver
    """
    # Exemple minimal – adapter proprement selon les besoins
    if action == "read_text":
        content = fs_driver.read_text(params["path"])
        return {"ok": True, "content": content}

    if action == "write_text":
        fs_driver.write_text(
            params["path"],
            params.get("content", ""),
            overwrite=params.get("overwrite", True),
        )
        return {"ok": True}

    if action == "append_text":
        fs_driver.append_text(params["path"], params.get("content", ""))
        return {"ok": True}

    if action == "list_dir":
        items = fs_driver.list_dir(params.get("path", ""))
        return {
            "ok": True,
            "items": [item.__dict__ for item in items],
        }

    if action == "make_dir":
        fs_driver.make_dir(params["path"], exist_ok=params.get("exist_ok", True))
        return {"ok": True}

    if action == "move_path":
        fs_driver.move_path(
            params["src"],
            params["dst"],
            overwrite=params.get("overwrite", False),
        )
        return {"ok": True}

    if action == "delete_path":
        fs_driver.delete_path(params["path"])
        return {"ok": True}

    if action == "stat_path":
        info = fs_driver.stat_path(params["path"])
        return {"ok": True, "info": info}

    if action == "search_text":
        results = fs_driver.search_text(
            query=params["query"],
            start_relative=params.get("path", ""),
            max_files=params.get("max_files", 100),
            extensions=params.get("extensions"),
        )
        return {"ok": True, "results": results}

    return {"ok": False, "error": f"Unknown fs action: {action}"}
```

💡 Si les helpers utilisent déjà un pattern de “router d’actions”, intégrer `execute_fs_action` dans ce pattern au lieu de faire un bloc isolé.

### 2.3. Orchestrateur : nouvelle intent `filesystem`

Dans `agents/orchestrator.py`, tu dois :

1. Étendre le **prompt système** pour expliquer au LLM comment utiliser le FS.
2. Étendre la **logique de parsing JSON** pour reconnaître `intent: "filesystem"`.

#### 2.3.1. Prompt – ajouter un bloc clair sur le FS

Dans la partie système où tu expliques les intentions possibles à Clara (là où on décrit déjà `memory_*`, etc.), ajouter un bloc du style :

```text
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

Actions supportées (génériques, sans cas particulier):
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
```

⚠️ Rester général, ne pas ajouter de cas “spéciaux” type “si Jérémy demande X…”.


#### 2.3.2. Parsing des intentions

Dans le code de l’orchestrateur qui parse le JSON renvoyé par le LLM (là où on gère déjà `memory_*`, etc.), ajouter une branche pour `intent == "filesystem"` :

```python
if intent == "filesystem":
    action = data.get("action")
    params = data.get("params") or {}
    fs_result = execute_fs_action(action, params)
    # intégrer fs_result dans le summary de cycle / logs
    # et préparer une réponse lisible pour l'utilisateur si nécessaire
```

Le but : 
- ne pas casser les autres intents,  
- mais permettre au LLM d’utiliser le FS quand c’est pertinent.


---

## 3. Logging

Objectif : suivre ce que fait Clara sur le FS, sans polluer la vue utilisateur.

1. Utiliser le logger défini dans `fs_driver.py` (`logger = logging.getLogger(__name__)`).  
2. S’assurer que la config globale de logging capture aussi les logs `drivers.fs_driver` dans `logs/sessions/...` (JSON ou texte, selon ce qui existe déjà).  
3. Ne pas logguer le contenu complet des fichiers volumineux, seulement :
   - l’action
   - le chemin relatif
   - éventuellement la taille / nb de résultats.

Exemples à viser dans les logs :

```json
{
  "component": "fs_driver",
  "action": "write_text",
  "path": "reports/2025-12-06_test_report.md"
}
```

---

## 4. Tests

Créer / compléter `tests/test_fs_driver.py` avec au minimum :

- création d’un FSDriver pointant vers un dossier temporaire (ex: `tmp_path` de pytest),
- tests pour :
  - `write_text` + `read_text`
  - `append_text`
  - `list_dir`
  - `make_dir`
  - `move_path`
  - `delete_path`
  - `stat_path`
  - `search_text`

Les tests doivent rester **généraux** et **sans connaissance métier**.


---

## 5. Discipline / journaux

Comme d’habitude :

1. Documenter cette intervention dans :  
   `journal/cursor_gpt/2025-12-06_fs_driver_full_power.md`  
   avec :
   - Contexte
   - Changements effectués
   - Fichiers touchés
   - Tests réalisés
   - Limites / TODO éventuels (ex: PDF à traiter plus tard)

2. Ne pas modifier les logs runtime dans `logs/sessions/` à la main.

3. Faire un commit propre, par exemple :  
   `feat(fs): add full filesystem driver and orchestrator integration`

Fin du patch.
