# Clara - Contacts Helpers
"""
Helpers pour la gestion des contacts structurés
Utilise la table contacts dédiée (pas la table memory)
"""

import json
import sqlite3
import logging
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = "memory/memory.sqlite"


def save_contact(contact: dict) -> int:
    """
    Sauvegarde un contact dans la table contacts dédiée
    
    Args:
        contact: Dict avec structure contact (first_name, last_name, etc.)
    
    Returns:
        ID du contact créé
    """
    # Normaliser le contact
    normalized = _normalize_contact(contact)
    
    # Générer des tags depuis le contact
    tags = _generate_contact_tags(normalized)
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contacts (
                    first_name, last_name, display_name, aliases, category,
                    relationship, phones, emails, company, role, notes,
                    whatsapp_number, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                normalized.get('first_name'),
                normalized.get('last_name'),
                normalized.get('display_name'),
                json.dumps(normalized.get('aliases', [])),
                normalized.get('category', 'other'),
                json.dumps(normalized.get('relationship', {})) if isinstance(normalized.get('relationship'), dict) else normalized.get('relationship', ''),
                json.dumps(normalized.get('phones', [])),
                json.dumps(normalized.get('emails', [])),
                normalized.get('company'),
                normalized.get('role'),
                json.dumps(normalized.get('notes', [])),
                normalized.get('whatsapp_number'),
                json.dumps(tags)
            ))
            conn.commit()
            contact_id = cursor.lastrowid
            logger.debug(f"Contact sauvegardé: id={contact_id}, name={normalized.get('display_name')}")
            return contact_id
    except Exception as e:
        logger.exception(f"save_contact failed: {e}")
        raise


def update_contact(contact_id: int, updates: dict) -> None:
    """
    Met à jour un contact existant dans la table contacts
    
    Args:
        contact_id: ID du contact à mettre à jour
        updates: Dict avec les champs à mettre à jour
    """
    # Récupérer le contact existant
    existing = get_contact_by_id(contact_id)
    if not existing:
        raise ValueError(f"Contact {contact_id} not found")
    
    # Appliquer les updates
    updated_data = existing.copy()
    updated_data.update(updates)
    
    # Normaliser
    normalized = _normalize_contact(updated_data)
    
    # Générer nouveaux tags
    tags = _generate_contact_tags(normalized)
    
    # Construire dynamiquement le SET
    set_clauses = []
    params = []
    
    if 'first_name' in updates:
        set_clauses.append("first_name = ?")
        params.append(normalized.get('first_name'))
    if 'last_name' in updates:
        set_clauses.append("last_name = ?")
        params.append(normalized.get('last_name'))
    if 'display_name' in updates or 'first_name' in updates or 'last_name' in updates:
        set_clauses.append("display_name = ?")
        params.append(normalized.get('display_name'))
    if 'aliases' in updates:
        set_clauses.append("aliases = ?")
        params.append(json.dumps(normalized.get('aliases', [])))
    if 'category' in updates:
        set_clauses.append("category = ?")
        params.append(normalized.get('category', 'other'))
    if 'relationship' in updates:
        rel = normalized.get('relationship', {})
        set_clauses.append("relationship = ?")
        params.append(json.dumps(rel) if isinstance(rel, dict) else rel)
    if 'phones' in updates:
        set_clauses.append("phones = ?")
        params.append(json.dumps(normalized.get('phones', [])))
    if 'emails' in updates:
        set_clauses.append("emails = ?")
        params.append(json.dumps(normalized.get('emails', [])))
    if 'company' in updates:
        set_clauses.append("company = ?")
        params.append(normalized.get('company'))
    if 'role' in updates:
        set_clauses.append("role = ?")
        params.append(normalized.get('role'))
    if 'notes' in updates:
        set_clauses.append("notes = ?")
        params.append(json.dumps(normalized.get('notes', [])))
    if 'whatsapp_number' in updates:
        set_clauses.append("whatsapp_number = ?")
        params.append(normalized.get('whatsapp_number'))
    
    # Toujours mettre à jour tags et updated_at
    set_clauses.append("tags = ?")
    params.append(json.dumps(tags))
    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
    
    params.append(contact_id)
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE contacts SET {', '.join(set_clauses)} WHERE id = ?",
                params
            )
            conn.commit()
            logger.debug(f"Contact mis à jour: id={contact_id}")
    except Exception as e:
        logger.exception(f"update_contact failed for id={contact_id}: {e}")
        raise


def get_contact_by_id(contact_id: int) -> Optional[dict]:
    """
    Récupère un contact par son ID
    
    Args:
        contact_id: ID du contact
    
    Returns:
        Dict avec le contact ou None
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        if row:
            return _row_to_contact_dict(row)
        return None


def find_contacts(query: str, limit: int = 50) -> list[dict]:
    """
    Recherche des contacts par nom, alias, email, téléphone, company
    
    Args:
        query: Texte à rechercher
        limit: Limite de résultats
    
    Returns:
        Liste de contacts (dicts parsés)
    """
    search_pattern = f"%{query}%"
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM contacts
            WHERE first_name LIKE ? OR last_name LIKE ? OR display_name LIKE ?
               OR aliases LIKE ? OR emails LIKE ? OR phones LIKE ? OR company LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (search_pattern, search_pattern, search_pattern, search_pattern, 
              search_pattern, search_pattern, search_pattern, limit))
        rows = cursor.fetchall()
        return [_row_to_contact_dict(row) for row in rows]


def get_all_contacts(limit: int = 100) -> list[dict]:
    """
    Récupère tous les contacts
    
    Args:
        limit: Limite de résultats
    
    Returns:
        Liste de contacts (dicts parsés)
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM contacts
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [_row_to_contact_dict(row) for row in rows]


def _normalize_contact(contact: dict) -> dict:
    """Normalise la structure d'un contact"""
    return {
        'first_name': contact.get('first_name', ''),
        'last_name': contact.get('last_name', ''),
        'display_name': contact.get('display_name', 
                                    f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()),
        'aliases': contact.get('aliases', []),
        'category': contact.get('category', 'other'),
        'relationship': contact.get('relationship', ''),
        'phones': contact.get('phones', []),
        'emails': contact.get('emails', []),
        'company': contact.get('company'),
        'role': contact.get('role'),
        'notes': contact.get('notes', []),
        'whatsapp_number': contact.get('whatsapp_number')
    }


def _generate_contact_tags(contact: dict) -> list[str]:
    """Génère des tags pour un contact"""
    tags = ["contact"]
    
    # Ajouter la catégorie
    if contact.get('category'):
        tags.append(contact['category'])
    
    # Ajouter la relation
    if contact.get('relationship'):
        rel = contact['relationship']
        if isinstance(rel, dict):
            if rel.get('category'):
                tags.append(rel['category'])
            if rel.get('role'):
                tags.append(rel['role'])
        elif isinstance(rel, str):
            tags.append(rel)
    
    # Ajouter la company si présente
    if contact.get('company'):
        tags.append(contact['company'].lower())
    
    # Ajouter les alias
    for alias in contact.get('aliases', []):
        tags.append(alias.lower())
    
    return list(set(tags))  # Dédupliquer


def _row_to_contact_dict(row: sqlite3.Row) -> dict:
    """Convertit une row SQLite en dict contact"""
    contact = dict(row)
    
    # Désérialiser les JSON
    for field in ['aliases', 'phones', 'emails', 'notes', 'tags']:
        if contact.get(field):
            try:
                contact[field] = json.loads(contact[field])
            except (json.JSONDecodeError, TypeError):
                contact[field] = []
        else:
            contact[field] = []
    
    # Désérialiser relationship si c'est un JSON
    if contact.get('relationship'):
        try:
            contact['relationship'] = json.loads(contact['relationship'])
        except (json.JSONDecodeError, TypeError):
            pass  # Garder comme string si ce n'est pas du JSON
    
    return contact
