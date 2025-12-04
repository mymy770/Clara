# Clara - Memory Core
"""
API de mémoire interne pour Clara
Stockage SQLite simple, sans logique métier
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional


def init_db(
    db_path: str = "memory/memory.sqlite",
    schema_path: str = "memory/schema.sql"
) -> None:
    """
    Initialise la base de données mémoire
    
    - Crée le dossier memory si nécessaire
    - Crée le fichier SQLite s'il n'existe pas
    - Applique le schéma SQL
    """
    # Créer le dossier si nécessaire
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Créer/ouvrir la base et appliquer le schéma
    with sqlite3.connect(str(db_file)) as conn:
        # Lire et exécuter le schéma
        schema_file = Path(schema_path)
        if schema_file.exists():
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = f.read()
            conn.executescript(schema)
            conn.commit()


def save_item(
    type: str,
    content: str,
    tags: Optional[list[str]] = None,
    db_path: str = "memory/memory.sqlite"
) -> int:
    """
    Sauvegarde un item en mémoire
    
    Args:
        type: Type d'item (contact, task, todo, preference, etc.)
        content: Contenu textuel de l'item
        tags: Liste de tags optionnels
        db_path: Chemin vers la base de données
    
    Returns:
        ID de l'item créé
    """
    tags_json = json.dumps(tags) if tags else None
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO memory (type, content, tags) VALUES (?, ?, ?)",
            (type, content, tags_json)
        )
        conn.commit()
        return cursor.lastrowid


def update_item(
    item_id: int,
    content: Optional[str] = None,
    tags: Optional[list[str]] = None,
    db_path: str = "memory/memory.sqlite"
) -> None:
    """
    Met à jour un item existant
    
    Args:
        item_id: ID de l'item à mettre à jour
        content: Nouveau contenu (si fourni)
        tags: Nouveaux tags (si fournis)
        db_path: Chemin vers la base de données
    """
    # Ne rien faire si aucun champ n'est fourni
    if content is None and tags is None:
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        if content is not None and tags is not None:
            tags_json = json.dumps(tags)
            cursor.execute(
                """UPDATE memory 
                   SET content = ?, tags = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                (content, tags_json, item_id)
            )
        elif content is not None:
            cursor.execute(
                """UPDATE memory 
                   SET content = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                (content, item_id)
            )
        elif tags is not None:
            tags_json = json.dumps(tags)
            cursor.execute(
                """UPDATE memory 
                   SET tags = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                (tags_json, item_id)
            )
        
        conn.commit()


def get_items(
    type: Optional[str] = None,
    limit: Optional[int] = None,
    db_path: str = "memory/memory.sqlite"
) -> list[dict]:
    """
    Récupère des items de la mémoire
    
    Args:
        type: Filtrer par type (si fourni)
        limit: Limiter le nombre de résultats (si fourni)
        db_path: Chemin vers la base de données
    
    Returns:
        Liste de dicts avec id, type, content, tags, created_at, updated_at
    """
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if type is not None:
            query = "SELECT * FROM memory WHERE type = ? ORDER BY created_at DESC"
            params = [type]
        else:
            query = "SELECT * FROM memory ORDER BY created_at DESC"
            params = []
        
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convertir en liste de dicts et désérialiser tags
        results = []
        for row in rows:
            item = dict(row)
            # Désérialiser tags
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            else:
                item['tags'] = []
            results.append(item)
        
        return results


def search_items(
    query: str,
    type: Optional[str] = None,
    db_path: str = "memory/memory.sqlite"
) -> list[dict]:
    """
    Recherche des items par contenu
    
    Args:
        query: Texte à rechercher dans le contenu
        type: Filtrer par type (si fourni)
        db_path: Chemin vers la base de données
    
    Returns:
        Liste de dicts avec id, type, content, tags, created_at, updated_at
    """
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_pattern = f"%{query}%"
        
        if type is not None:
            cursor.execute(
                "SELECT * FROM memory WHERE content LIKE ? AND type = ? ORDER BY created_at DESC",
                (search_pattern, type)
            )
        else:
            cursor.execute(
                "SELECT * FROM memory WHERE content LIKE ? ORDER BY created_at DESC",
                (search_pattern,)
            )
        
        rows = cursor.fetchall()
        
        # Convertir en liste de dicts et désérialiser tags
        results = []
        for row in rows:
            item = dict(row)
            # Désérialiser tags
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            else:
                item['tags'] = []
            results.append(item)
        
        return results


def delete_item(
    item_id: int,
    db_path: str = "memory/memory.sqlite"
) -> None:
    """
    Supprime un item de la mémoire
    
    Args:
        item_id: ID de l'item à supprimer
        db_path: Chemin vers la base de données
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory WHERE id = ?", (item_id,))
        conn.commit()
