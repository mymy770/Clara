# Clara - Auto-tagging
"""
Génération automatique de tags à partir du contenu
"""

import re


# Stopwords français basiques
STOPWORDS = {
    'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou', 'mais',
    'dans', 'pour', 'par', 'sur', 'avec', 'sans', 'sous', 'vers', 'chez',
    'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
    'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses',
    'ce', 'cet', 'cette', 'ces', 'qui', 'que', 'quoi', 'dont', 'où',
    'à', 'au', 'aux', 'en', 'y', 'a', 'ai', 'as', 'est', 'sont',
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had'
}


def generate_tags(content: str, max_tags: int = 5) -> list[str]:
    """
    Génère automatiquement des tags depuis le contenu
    
    Args:
        content: Texte du contenu
        max_tags: Nombre maximum de tags à générer
    
    Returns:
        Liste de tags (lowercase, sans stopwords)
    """
    if not content:
        return []
    
    # Nettoyer et tokenizer
    # Garder seulement les mots (enlever ponctuation)
    words = re.findall(r'\b[a-zàâäéèêëïîôùûüç]+\b', content.lower())
    
    # Filtrer les stopwords et les mots trop courts
    meaningful_words = [
        word for word in words 
        if word not in STOPWORDS and len(word) >= 3
    ]
    
    # Compter les occurrences
    word_counts = {}
    for word in meaningful_words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Trier par fréquence et prendre les N premiers
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    tags = [word for word, count in sorted_words[:max_tags]]
    
    return tags

