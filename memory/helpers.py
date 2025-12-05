# Clara - Memory Helpers
"""
Fonctions helper typées pour faciliter l'utilisation de la mémoire
"""

from memory.memory_core import save_item
from memory.tagging import generate_tags


def save_note(content: str, tags: list[str] | None = None) -> int:
    """Sauvegarde une note en mémoire (avec auto-tagging si tags=None)"""
    if tags is None:
        tags = generate_tags(content)
    # S'assurer qu'on a au moins un tag
    if not tags:
        tags = ["note"]
    return save_item(type="note", content=content, tags=tags)


def save_process(content: str, tags: list[str] | None = None) -> int:
    """Sauvegarde un processus en mémoire (avec auto-tagging si tags=None)"""
    if tags is None:
        tags = generate_tags(content)
    # S'assurer qu'on a au moins un tag
    if not tags:
        tags = ["process"]
    return save_item(type="process", content=content, tags=tags)


def save_protocol(content: str, tags: list[str] | None = None) -> int:
    """Sauvegarde un protocole en mémoire (avec auto-tagging si tags=None)"""
    if tags is None:
        tags = generate_tags(content)
    # S'assurer qu'on a au moins un tag
    if not tags:
        tags = ["protocol"]
    return save_item(type="protocol", content=content, tags=tags)


def save_todo(content: str, tags: list[str] | None = None) -> int:
    """Sauvegarde un todo en mémoire (avec auto-tagging si tags=None)"""
    if tags is None:
        tags = generate_tags(content)
    # S'assurer qu'on a au moins un tag
    if not tags:
        tags = ["todo"]
    return save_item(type="todo", content=content, tags=tags)

