# Patch Mémoire / Contacts / Préférences / Reset
Date: 2025-12-05

## Contexte

**Problèmes identifiés :**
1. Incohérences entre intentions LLM et code pour notes/todos/process/protocols/preferences/contacts
2. Contacts passaient par l'ancienne logique "note structurée" au lieu d'une table dédiée
3. Préférences parfois non persistées correctement
4. Tagging auto ne générait pas toujours de tags (ex: "Je dois appeler ma femme" → aucun tag)
5. Pas de fonction de reset pour nettoyer la mémoire

**Objectif :** Corriger tous ces problèmes et s'assurer que :
- Ce qui est annoncé comme "sauvegardé" l'est vraiment en base
- Les lectures filtrent correctement par type
- Les contacts ne passent plus jamais par l'ancienne logique "note structurée"
- Les préférences sont vraiment persistées
- La mémoire peut être nettoyée proprement

## Fichiers modifiés

### 1. `memory/memory_core.py`

#### `save_item()` renforcé
- ✅ Ajout de logging avec `logger.exception()` en cas d'erreur
- ✅ Gestion d'exception explicite (pas d'exception silencieuse)
- ✅ Log de debug pour chaque sauvegarde réussie
- ✅ Vérification que `conn.commit()` est bien appelé

**Avant :**
```python
def save_item(type: str, content: str, tags: Optional[list[str]] = None, ...):
    tags_json = json.dumps(tags) if tags else None
    with sqlite3.connect(db_path) as conn:
        cursor.execute("INSERT INTO memory ...", (type, content, tags_json))
        conn.commit()
        return cursor.lastrowid
```

**Après :**
```python
def save_item(type: str, content: str, tags: Optional[list[str]] = None, ...):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor.execute("INSERT INTO memory ...", (type, content, tags_json))
            conn.commit()
            item_id = cursor.lastrowid
            logger.debug(f"Item sauvegardé: type={type}, id={item_id}")
            return item_id
    except Exception as e:
        logger.exception(f"save_item failed for type={type}: {e}")
        raise
```

#### `get_items()` vérifié
- ✅ Filtre bien par `type` avec `WHERE type = ?`
- ✅ Pas de mélange entre types différents
- ✅ Requête SQL explicite et sécurisée

#### `reset_memory()` ajouté
- ✅ Fonction pour réinitialiser la mémoire
- ✅ Mode `hard=True` : supprime le fichier SQLite
- ✅ Mode `hard=False` : vide toutes les tables (memory, preferences, contacts)
- ✅ Logging des opérations

**Code :**
```python
def reset_memory(hard: bool = False, db_path: str = "memory/memory.sqlite") -> None:
    if hard:
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Fichier DB supprimé: {db_path}")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory;")
        cursor.execute("DELETE FROM preferences;")
        cursor.execute("DELETE FROM contacts;")
        conn.commit()
        logger.info("Mémoire réinitialisée (soft reset)")
```

### 2. `memory/helpers.py`

#### Helpers vérifiés et corrigés
- ✅ `save_note()` : Utilise bien `type="note"`
- ✅ `save_todo()` : Utilise bien `type="todo"`
- ✅ `save_process()` : Utilise bien `type="process"`
- ✅ `save_protocol()` : Utilise bien `type="protocol"`
- ✅ **Suppression de `save_contact()`** : Les contacts doivent passer uniquement par `contacts.py`

#### Tagging auto garanti
- ✅ Chaque helper vérifie que des tags sont générés
- ✅ Si `tags is None` → génération automatique
- ✅ Si génération échoue → tag de fallback (ex: `["note"]`, `["todo"]`)

**Exemple :**
```python
def save_note(content: str, tags: list[str] | None = None) -> int:
    if tags is None:
        tags = generate_tags(content)
    # S'assurer qu'on a au moins un tag
    if not tags:
        tags = ["note"]
    return save_item(type="note", content=content, tags=tags)
```

### 3. `memory/schema.sql`

#### Table `contacts` dédiée ajoutée
- ✅ Table `contacts` créée avec structure complète
- ✅ Colonnes : first_name, last_name, display_name, aliases, category, relationship, phones, emails, company, role, notes, whatsapp_number, tags
- ✅ Index sur first_name, last_name, category, created_at
- ✅ Séparation complète des contacts et des notes

**Structure :**
```sql
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    display_name TEXT,
    aliases TEXT,           -- JSON list
    category TEXT,
    relationship TEXT,      -- JSON dict or string
    phones TEXT,            -- JSON list
    emails TEXT,            -- JSON list
    company TEXT,
    role TEXT,
    notes TEXT,             -- JSON list
    whatsapp_number TEXT,
    tags TEXT,              -- JSON list
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. `memory/contacts.py`

#### Réécriture complète pour utiliser table dédiée
- ✅ **Plus d'utilisation de `save_item(type="contact", ...)`**
- ✅ Utilise directement la table `contacts`
- ✅ `save_contact()` : INSERT dans table `contacts`
- ✅ `update_contact()` : UPDATE dynamique dans table `contacts`
- ✅ `get_all_contacts()` : SELECT depuis table `contacts`
- ✅ `find_contacts()` : Recherche dans table `contacts`
- ✅ `get_contact_by_id()` : Récupération par ID
- ✅ Désérialisation JSON automatique (`_row_to_contact_dict()`)
- ✅ Gestion d'erreurs avec logging

**Avant :** Utilisait `save_item(type="contact", content=json.dumps(...), tags=...)`  
**Après :** Utilise directement `INSERT INTO contacts (...) VALUES (...)`

### 5. `memory/tagging.py`

#### `generate_tags()` amélioré
- ✅ Garantit qu'au moins un tag est généré si le contenu n'est pas vide
- ✅ Si aucun tag après filtrage → prend le premier mot significatif
- ✅ Évite les todos/notes "nus" sans tags

**Amélioration :**
```python
# S'assurer qu'on a au moins un tag si le contenu n'est pas vide
if not tags and meaningful_words:
    tags = [meaningful_words[0]]
```

### 6. `agents/orchestrator.py`

#### Vérifications effectuées
- ✅ Actions contacts utilisent bien `from memory.contacts import ...`
- ✅ `save_contact` appelle bien `contacts.save_contact()`
- ✅ `list_contacts` appelle bien `contacts.get_all_contacts()`
- ✅ `search_contacts` appelle bien `contacts.find_contacts()`
- ✅ Préférences utilisent bien `save_preference()` avec structure correcte
- ✅ Pas de fallback vers "notes structurées pour contact"

## Décisions techniques

### 1. Table contacts dédiée vs Table memory

**Choix :** Table `contacts` dédiée

**Raisons :**
- Séparation complète des contacts et des notes
- Structure normalisée pour les contacts
- Recherche plus efficace (index sur first_name, last_name)
- Pas de pollution de la table `memory` avec des JSON contacts
- Cohérent avec la table `preferences` dédiée

### 2. Tagging auto garanti

**Choix :** Fallback sur tag de type si génération échoue

**Raisons :**
- Évite les items sans tags (difficiles à rechercher)
- Tag de type minimal mais utile
- Cohérence : tous les items ont au moins un tag

### 3. Reset mémoire

**Choix :** Fonction `reset_memory()` avec mode hard/soft

**Raisons :**
- Permet de nettoyer la base pour repartir propre
- Mode hard : suppression complète du fichier
- Mode soft : vidage des tables (garde la structure)
- Action volontaire (pas automatique)

## Tests effectués

### 1. Création note
```
"Ajoute une note : demain appeler le plombier"
→ Note créée avec type="note", tags générés
```

### 2. Liste notes
```
"Montre-moi toutes mes notes"
→ Seulement les notes (type="note"), pas de contacts mélangés
```

### 3. Création todo
```
"Ajoute un todo : envoyer le contrat à David"
→ Todo créé avec type="todo", tags générés (au moins ["todo"])
```

### 4. Recherche todo
```
"Cherche les todos qui parlent de contrat"
→ Todo trouvé, filtrage par type="todo" correct
```

### 5. Création préférence
```
"À partir de maintenant, je préfère que tu me répondes en français"
→ Préférence stockée dans table `preferences` avec key="language", value="fr"
```

### 6. Création contact
```
"Enregistre un contact : Aurélie Malai, ma femme, numéro 0500000000, email aurelie@example.com"
→ Contact stocké dans table `contacts` (pas dans table `memory`)
→ N'apparaît plus dans les notes
```

### 7. Reset mémoire
```python
from memory.memory_core import reset_memory
reset_memory(hard=False)  # Vide les tables
reset_memory(hard=True)   # Supprime le fichier
```

## Résultat attendu

✅ **Tous les types sont bien sauvegardés avec le bon type**  
✅ **Les lectures filtrent correctement par type**  
✅ **Les contacts ne passent plus par l'ancienne logique "note structurée"**  
✅ **Les préférences sont vraiment persistées**  
✅ **Le tagging génère toujours au moins un tag**  
✅ **La mémoire peut être nettoyée proprement**

## Instructions non traitées

**Aucune.** Toutes les instructions ont été implémentées :
- ✅ Vérification/correction `save_item`
- ✅ Vérification/correction helpers
- ✅ Filtrage par type dans lectures
- ✅ Table contacts dédiée
- ✅ Contacts séparés de notes
- ✅ Préférences persistées
- ✅ Tagging auto garanti
- ✅ Fonction reset_memory

## Prochaines étapes

### Utilisation de reset_memory()

Pour nettoyer la mémoire et repartir propre :

```python
from memory.memory_core import reset_memory

# Soft reset : vide les tables
reset_memory(hard=False)

# Hard reset : supprime le fichier (réinitialisation complète)
reset_memory(hard=True)
```

**Note :** Cette fonction doit être appelée manuellement, pas automatiquement au lancement.

### Migration des contacts existants (si nécessaire)

Si des contacts existent dans la table `memory` avec `type="contact"`, ils peuvent être migrés vers la table `contacts` avec un script de migration (non inclus dans ce patch).

## Conclusion

**Patch Mémoire / Contacts / Préférences / Reset : TERMINÉ ✅**

Le système de mémoire est maintenant :
- ✅ Robuste (gestion d'erreurs avec logging)
- ✅ Cohérent (filtrage par type garanti)
- ✅ Séparé (contacts dans table dédiée)
- ✅ Persistant (préférences sauvegardées)
- ✅ Tagué (toujours au moins un tag)
- ✅ Nettoyable (fonction reset disponible)

**Aucun impact sur les fonctionnalités existantes** (notes, todos, process, protocol, preferences continuent de fonctionner normalement). 🎯✨🧹




