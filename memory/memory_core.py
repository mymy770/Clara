# Clara - Memory Core
"""
API de mémoire interne pour Clara
Stockage SQLite simple, sans logique métier
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


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
        type: Type d'item (note, todo, process, protocol, etc.)
        content: Contenu textuel de l'item
        tags: Liste de tags optionnels
        db_path: Chemin vers la base de données
    
    Returns:
        ID de l'item créé
    
    Raises:
        Exception: Si la sauvegarde échoue (loggée avant de lever)
    """
    tags_json = json.dumps(tags) if tags else None
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memory (type, content, tags) VALUES (?, ?, ?)",
                (type, content, tags_json)
            )
            conn.commit()
            item_id = cursor.lastrowid
            logger.debug(f"Item sauvegardé: type={type}, id={item_id}")
            return item_id
    except Exception as e:
        logger.exception(f"save_item failed for type={type}: {e}")
        raise


def update_item(
    item_id: int,
    content: Optional[str] = None,
    tags: Optional[list[str]] = None,
    db_path: str = "memory/memory.sqlite"
) -> bool:
    """
    Met à jour un item existant
    
    Args:
        item_id: ID de l'item à mettre à jour
        content: Nouveau contenu (si fourni)
        tags: Nouveaux tags (si fournis)
        db_path: Chemin vers la base de données
    
    Returns:
        True si l'item a été mis à jour, False si l'item n'existe pas
    """
    # Ne rien faire si aucun champ n'est fourni
    if content is None and tags is None:
        return False
    
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
        
        # Retourner True si une ligne a été modifiée
        return cursor.rowcount > 0


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


# ============================================
# FONCTIONS PRÉFÉRENCES
# ============================================

def save_preference(pref: dict, db_path: str = "memory/memory.sqlite") -> bool:
    """
    Insère ou met à jour une préférence selon key+scope+agent
    
    Args:
        pref: Dict avec structure préférence :
            - scope: "global" | "agent"
            - agent: "mail" | "calendar" | "orchestrator" | null
            - domain: "communication" | "ui" | "agenda" | ...
            - key: string (unique)
            - value: string
            - source: "user" | "inferred"
            - confidence: float (0.0-1.0)
        db_path: Chemin vers la base de données
    
    Returns:
        True si succès, False sinon
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Vérifier si une préférence existe déjà avec cette key
            cursor.execute("SELECT id FROM preferences WHERE key = ?", (pref.get('key'),))
            existing = cursor.fetchone()
            
            if existing:
                # UPDATE
                cursor.execute("""
                    UPDATE preferences 
                    SET scope = ?, agent = ?, domain = ?, value = ?, 
                        source = ?, confidence = ?
                    WHERE key = ?
                """, (
                    pref.get('scope'),
                    pref.get('agent'),
                    pref.get('domain'),
                    pref.get('value'),
                    pref.get('source', 'user'),
                    pref.get('confidence', 1.0),
                    pref.get('key')
                ))
            else:
                # INSERT
                cursor.execute("""
                    INSERT INTO preferences (scope, agent, domain, key, value, source, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    pref.get('scope', 'global'),
                    pref.get('agent'),
                    pref.get('domain'),
                    pref.get('key'),
                    pref.get('value'),
                    pref.get('source', 'user'),
                    pref.get('confidence', 1.0)
                ))
            
            conn.commit()
            return True
    except Exception:
        return False


def get_preference_by_key(key: str, db_path: str = "memory/memory.sqlite") -> Optional[dict]:
    """
    Retourne la préférence correspondant à key
    
    Args:
        key: Clé de la préférence
        db_path: Chemin vers la base de données
    
    Returns:
        Dict avec la préférence ou None
    """
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM preferences WHERE key = ?", (key,))
        row = cursor.fetchone()
        return dict(row) if row else None


def list_preferences(db_path: str = "memory/memory.sqlite") -> list[dict]:
    """
    Liste toutes les préférences stockées
    
    Args:
        db_path: Chemin vers la base de données
    
    Returns:
        Liste de dicts avec toutes les préférences
    """
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM preferences ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def search_preferences(query: str, db_path: str = "memory/memory.sqlite") -> list[dict]:
    """
    Recherche textuelle dans key/value/domain
    
    Args:
        query: Texte à rechercher
        db_path: Chemin vers la base de données
    
    Returns:
        Liste de dicts avec les préférences trouvées
    """
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT * FROM preferences 
            WHERE key LIKE ? OR value LIKE ? OR domain LIKE ?
            ORDER BY created_at DESC
        """, (search_pattern, search_pattern, search_pattern))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# ============================================
# FONCTION RESET MÉMOIRE
# ============================================

def reset_memory(hard: bool = False, db_path: str = "memory/memory.sqlite") -> None:
    """
    Réinitialise la mémoire de Clara
    
    Args:
        hard: Si True, supprime aussi le fichier SQLite (réinitialisation complète)
        db_path: Chemin vers la base de données
    """
    import os
    
    if hard:
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Fichier DB supprimé: {db_path}")
        return
    
    # Soft reset : vider les tables
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Vider toutes les tables
            cursor.execute("DELETE FROM memory;")
            cursor.execute("DELETE FROM preferences;")
            cursor.execute("DELETE FROM contacts;")
            conn.commit()
            logger.info("Mémoire réinitialisée (soft reset)")
    except Exception as e:
        logger.exception(f"reset_memory failed: {e}")
        raise
