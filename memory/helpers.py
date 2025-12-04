# Clara - Memory Helpers
"""
Fonctions helper typées pour faciliter l'utilisation de la mémoire
"""

from memory.memory_core import save_item


def save_note(content: str, tags: list[str] | None = None) -> int:
    """Sauvegarde une note en mémoire"""
    return save_item(type="note", content=content, tags=tags)


def save_process(content: str, tags: list[str] | None = None) -> int:
    """Sauvegarde un processus en mémoire"""
    return save_item(type="process", content=content, tags=tags)


def save_protocol(content: str, tags: list[str] | None = None) -> int:
    """Sauvegarde un protocole en mémoire"""
    return save_item(type="protocol", content=content, tags=tags)


def save_todo(content: str, tags: list[str] | None = None) -> int:
    """Sauvegarde un todo en mémoire"""
    return save_item(type="todo", content=content, tags=tags)


def save_contact(content: str, tags: list[str] | None = None) -> int:
    """Sauvegarde un contact en mémoire"""
    return save_item(type="contact", content=content, tags=tags)

