# Clara - Driver Filesystem
"""
Driver filesystem sûr et générique pour Clara.
Toutes les opérations sont confinées sous root_path.
"""

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
