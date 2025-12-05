# Phase 2 : Implémentation Système Préférences
Date: 2025-12-05

## Contexte

Mission : Implémenter totalement le système de "préférences" dans la mémoire Clara, avec un modèle stable, propre et cohérent, sans impact sur les autres fonctionnalités (contacts, notes, todos).

## Fichiers modifiés

### 1. `memory/schema.sql`

**Ajout :** Table `preferences` avec structure complète

```sql
CREATE TABLE IF NOT EXISTS preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scope TEXT,
    agent TEXT,
    domain TEXT,
    key TEXT UNIQUE,
    value TEXT,
    source TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Index ajoutés :**
- `idx_preferences_key` : Recherche rapide par clé
- `idx_preferences_scope` : Filtrage par scope
- `idx_preferences_agent` : Filtrage par agent

**Impact :** Aucun impact sur les tables existantes (memory, etc.)

### 2. `memory/memory_core.py`

**Ajout :** 4 nouvelles fonctions pour gérer les préférences

#### `save_preference(pref: dict) -> bool`
- Insère ou met à jour une préférence selon `key+scope+agent`
- Vérifie l'existence via `key` (UNIQUE)
- Si existe → UPDATE
- Si n'existe pas → INSERT
- Retourne `True/False` selon succès

**Structure préférence attendue :**
```python
{
    'scope': 'global' | 'agent',
    'agent': 'mail' | 'calendar' | 'orchestrator' | None,
    'domain': 'communication' | 'ui' | 'agenda' | ...,
    'key': str (unique),
    'value': str,
    'source': 'user' | 'inferred',
    'confidence': float (0.0-1.0)
}
```

#### `get_preference_by_key(key: str) -> Optional[dict]`
- Retourne la préférence correspondant à `key`
- Retourne `None` si non trouvée

#### `list_preferences() -> list[dict]`
- Liste toutes les préférences stockées
- Triées par `created_at DESC`

#### `search_preferences(query: str) -> list[dict]`
- Recherche textuelle dans `key`, `value`, `domain`
- Utilise `LIKE` avec pattern `%query%`

**Philosophie :** Même structure que `save_note()`, `save_contact()`, etc.

### 3. `agents/orchestrator.py`

**Modifications :**

#### Import ajouté
```python
from memory.memory_core import ..., save_preference
```

#### Prompt système mis à jour
- Ajout section "PRÉFÉRENCES" dans les capacités mémoire
- Mention de `memory_set_preference`
- Instructions pour détecter expressions de préférences

#### Détection d'intentions préférences
**Méthode :** `_check_memory_read_intent()` étendue

**Mots-clés détectés :**
- "je préfère", "je préférerais", "préfère", "préférerais"
- "désormais", "à partir de maintenant", "dorénavant"
- "toujours", "jamais", "ne jamais"
- "souhaite que", "veux que"

**Exemple :**
```
"À partir de maintenant, parle toujours en français"
→ Intention détectée : set_preference
```

#### Exécution intention `set_preference`
**Méthode :** `_process_memory_action()` étendue

**Logique :**
1. Parse le JSON d'intention avec `key`, `value`, `scope`, `agent`, `domain`
2. Appelle `save_preference(pref_dict)`
3. Si succès :
   - Sauvegarde aussi dans `memory` (table générale) avec tags automatiques
   - Tags : `["preference", domain, agent or "global"]`
   - Retourne message de confirmation
4. Si erreur : Message d'erreur

**Exemple JSON intention :**
```json
{
  "memory_action": "set_preference",
  "key": "language",
  "value": "fr",
  "scope": "global",
  "agent": "orchestrator",
  "domain": "communication",
  "source": "user",
  "confidence": 1.0
}
```

### 4. `tests/test_memory_core.py`

**Ajout :** Test complet `test_preference_write_read()`

**Tests couverts :**
- ✅ Création préférence
- ✅ Lecture par clé
- ✅ Vérification tous les champs (key, value, scope, agent, domain)
- ✅ UPDATE (même key → remplace)
- ✅ `list_preferences()` : Liste complète
- ✅ `search_preferences()` : Recherche textuelle

**Schéma de test :** Table `preferences` ajoutée au schéma temporaire

## Décisions techniques

### 1. Table dédiée vs JSON dans memory

**Choix :** Table dédiée `preferences`

**Raisons :**
- Structure normalisée (scope, agent, domain, key, value)
- Recherche efficace (index sur key, scope, agent)
- Pas de parsing JSON nécessaire
- Cohérent avec le modèle SQLite

### 2. Double stockage (preferences + memory)

**Choix :** Sauvegarder dans `preferences` ET `memory` (avec tags)

**Raisons :**
- `preferences` : Accès rapide structuré
- `memory` : Historique et recherche globale
- Tags automatiques pour cohérence

### 3. Détection simple vs LLM parsing

**Choix :** Détection par mots-clés + LLM pour parsing fin

**Raisons :**
- Détection rapide côté orchestrator
- LLM génère JSON structuré avec tous les champs
- Pas de confirmation sauf ambiguïté (comme demandé)

### 4. Key UNIQUE vs composite (key+scope+agent)

**Choix :** `key` UNIQUE simple

**Raisons :**
- Simplicité
- Une préférence = une clé unique
- UPDATE automatique si même key

**Note :** Si besoin futur de préférences multiples par key (ex: key="language" pour différents agents), on pourra modifier le schéma.

## Instructions non traitées

**Aucune.** Toutes les instructions de la mission ont été implémentées :
- ✅ Table preferences dans schema.sql
- ✅ Helpers dans memory_core.py
- ✅ Détection dans orchestrator
- ✅ Exécution intention set_preference
- ✅ Tags automatiques
- ✅ Tests complets
- ✅ Documentation

## Prochaines étapes

### Phase 2 complète ✅

Le système de préférences est maintenant **100% fonctionnel** :
- ✅ Stockage SQLite structuré
- ✅ API complète (save, get, list, search)
- ✅ Détection automatique dans orchestrator
- ✅ Exécution sans confirmation
- ✅ Tests validés
- ✅ Documentation complète

### Intégrations futures possibles

1. **Phase 3 (UI Admin)** : Interface pour visualiser/modifier préférences
2. **Phase 4 (Agents outils)** : Utilisation des préférences par mail/calendar agents
3. **Phase 5 (Automatisation)** : Inférence automatique de préférences (source="inferred")

### Améliorations possibles

1. **Préférences par agent :** Modifier schéma pour permettre key+agent composite
2. **Validation :** Ajouter validation des valeurs (ex: language doit être "fr"|"en"|...)
3. **Confidence tracking :** Historique des changements de confidence
4. **Préférences par domaine :** Groupement par domain pour affichage

## Conclusion

**Mission Phase 2 Préférences : TERMINÉE ✅**

Le système est prêt pour utilisation immédiate. Clara peut maintenant :
- Détecter les expressions de préférences
- Enregistrer les préférences structurées
- Les récupérer rapidement
- Les utiliser dans les phases futures

**Aucun impact sur les fonctionnalités existantes** (notes, todos, contacts, process, protocol). 🎯✨

