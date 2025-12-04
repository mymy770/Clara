"""
Clara V3 - Driver Filesystem
Driver bas niveau pour l'accès aux fichiers et dossiers
"""

import os
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class FSDriver:
    """
    Driver pour les opérations filesystem
    Interface bas niveau pour lire/écrire/lister fichiers
    """
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path.home()
        logger.info(f"FS Driver initialized with base path: {self.base_path}")
    
    def list_dir(self, path: str) -> List[str]:
        """Liste le contenu d'un répertoire"""
        full_path = self._resolve_path(path)
        try:
            items = os.listdir(full_path)
            logger.debug(f"Listed {len(items)} items in {full_path}")
            return items
        except Exception as e:
            logger.error(f"Error listing directory {full_path}: {e}")
            raise
    
    def read_file(self, filepath: str) -> str:
        """Lit le contenu d'un fichier"""
        full_path = self._resolve_path(filepath)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Read {len(content)} bytes from {full_path}")
            return content
        except Exception as e:
            logger.error(f"Error reading file {full_path}: {e}")
            raise
    
    def write_file(self, filepath: str, content: str):
        """Écrit du contenu dans un fichier"""
        full_path = self._resolve_path(filepath)
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"Wrote {len(content)} bytes to {full_path}")
        except Exception as e:
            logger.error(f"Error writing file {full_path}: {e}")
            raise
    
    def file_exists(self, filepath: str) -> bool:
        """Vérifie si un fichier existe"""
        full_path = self._resolve_path(filepath)
        return full_path.exists()
    
    def _resolve_path(self, path: str) -> Path:
        """Résout un chemin relatif ou absolu"""
        p = Path(path)
        if p.is_absolute():
            return p
        return self.base_path / p

