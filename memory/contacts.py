# Clara - Contacts Helpers
"""
Helpers pour la gestion des contacts structurés
"""

import json
from typing import Optional
from memory.memory_core import save_item, search_items, get_items, update_item


def save_contact(contact: dict) -> int:
    """
    Sauvegarde un contact en mémoire
    
    Args:
        contact: Dict avec structure contact (first_name, last_name, etc.)
    
    Returns:
        ID du contact créé
    """
    # Normaliser le contact
    normalized = _normalize_contact(contact)
    
    # Sérialiser en JSON
    content_json = json.dumps(normalized, ensure_ascii=False)
    
    # Générer des tags depuis le contact
    tags = _generate_contact_tags(normalized)
    
    # Sauvegarder
    return save_item(type="contact", content=content_json, tags=tags)


def update_contact(contact_id: int, updates: dict) -> None:
    """
    Met à jour un contact existant
    
    Args:
        contact_id: ID du contact à mettre à jour
        updates: Dict avec les champs à mettre à jour
    """
    # Récupérer le contact existant
    contacts = get_items(type="contact")
    existing = None
    for c in contacts:
        if c['id'] == contact_id:
            existing = c
            break
    
    if not existing:
        raise ValueError(f"Contact {contact_id} not found")
    
    # Parser le contenu JSON
    contact_data = json.loads(existing['content'])
    
    # Appliquer les updates
    contact_data.update(updates)
    
    # Normaliser
    normalized = _normalize_contact(contact_data)
    
    # Sérialiser
    content_json = json.dumps(normalized, ensure_ascii=False)
    
    # Générer nouveaux tags
    tags = _generate_contact_tags(normalized)
    
    # Mettre à jour
    update_item(item_id=contact_id, content=content_json, tags=tags)


def find_contacts(query: str) -> list[dict]:
    """
    Recherche des contacts par nom, alias, email, téléphone, company
    
    Args:
        query: Texte à rechercher
    
    Returns:
        Liste de contacts (dicts parsés)
    """
    # Rechercher dans tous les contacts
    results = search_items(query=query, type="contact")
    
    # Parser les JSON
    parsed_contacts = []
    for item in results:
        contact_data = json.loads(item['content'])
        contact_data['id'] = item['id']
        contact_data['created_at'] = item['created_at']
        contact_data['updated_at'] = item['updated_at']
        parsed_contacts.append(contact_data)
    
    return parsed_contacts


def get_all_contacts(limit: int = 100) -> list[dict]:
    """
    Récupère tous les contacts
    
    Returns:
        Liste de contacts (dicts parsés)
    """
    results = get_items(type="contact", limit=limit)
    
    # Parser les JSON
    parsed_contacts = []
    for item in results:
        contact_data = json.loads(item['content'])
        contact_data['id'] = item['id']
        contact_data['created_at'] = item['created_at']
        contact_data['updated_at'] = item['updated_at']
        parsed_contacts.append(contact_data)
    
    return parsed_contacts


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
        'notes': contact.get('notes', [])
    }


def _generate_contact_tags(contact: dict) -> list[str]:
    """Génère des tags pour un contact"""
    tags = []
    
    # Ajouter la catégorie
    if contact.get('category'):
        tags.append(contact['category'])
    
    # Ajouter la relation
    if contact.get('relationship'):
        tags.append(contact['relationship'])
    
    # Ajouter la company si présente
    if contact.get('company'):
        tags.append(contact['company'].lower())
    
    # Ajouter les alias
    for alias in contact.get('aliases', []):
        tags.append(alias.lower())
    
    return list(set(tags))  # Dédupliquer

