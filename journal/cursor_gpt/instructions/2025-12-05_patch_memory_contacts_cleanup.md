# 2025-12-05 — Patch mémoire / contacts / préférences / reset
# Pour Cursor – Projet Clara

## 🎯 Objectif global

1. Corriger les incohérences entre intentions LLM et code pour :
   - NOTES
   - TODOS
   - PROCESS
   - PROTOCOLS
   - PREFERENCES
   - CONTACTS
2. S’assurer que :
   - ce qui est annoncé comme “sauvegardé” l’est vraiment en base,
   - les lectures filtrent correctement par type,
   - les contacts ne passent plus jamais par l’ancienne logique “note structurée”,
   - les préférences sont vraiment persistées,
   - la mémoire est nettoyée une bonne fois pour repartir propre.
3. Ne toucher qu’aux fichiers suivants :
   - `memory/memory_core.py`
   - `memory/helpers.py`
   - `memory/contacts.py`
   - `memory/tagging.py`
   - `agents/orchestrator.py`
   - (optionnel) `memory/schema.sql` pour nettoyage / cohérence.

À la fin, ajouter une entrée de journal dans `journal/cursor_gpt/` décrivant ce patch.

---

## 1️⃣ NOTES / TODOS / PROCESS / PROTOCOLS

### 1.1 Vérifier / corriger `save_item` dans `memory/memory_core.py`

Objectif : s’assurer que **tous** les types (`note`, `todo`, `process`, `protocol`) sont bien sauvegardés avec le bon type et commit.

- Ouvrir `memory/memory_core.py`.
- Localiser la fonction générique de sauvegarde (ex: `save_item` ou équivalent).
- Vérifier que :
  - le champ `type` est bien écrit dans la colonne prévue (souvent `type` ou `item_type`),
  - `conn.commit()` est bien appelé après l’insert,
  - aucune exception silencieuse ne peut “manger” l’erreur (au minimum, logger l’exception).

Si besoin, renforcer la fonction ainsi (pseudo-code, à adapter à la version existante) :

```python
def save_item(item_type: str, content: str, tags: list[str] | None = None, extra: dict | None = None) -> int:
    if tags is None:
        tags = []
    tags_json = json.dumps(tags)
    extra_json = json.dumps(extra or {})
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO items (type, content, tags, extra)
                VALUES (?, ?, ?, ?)
                """,
                (item_type, content, tags_json, extra_json),
            )
            conn.commit()
            return cur.lastrowid
    except Exception as e:
        # IMPORTANT : logger clairement l’erreur
        logger.exception(f"save_item failed for type={item_type}: {e}")
        raise
```

Assurer que les colonnes (`type`, `content`, `tags`, `extra`) correspondent à la structure réelle de la table `items` dans `schema.sql`.

---

### 1.2 Vérifier / corriger les helpers dans `memory/helpers.py`

Objectif : chaque helper doit appeler `save_item` avec le **bon type** et ne rien filtrer de travers.

- Ouvrir `memory/helpers.py`.
- Vérifier que :

```python
def save_note(content: str, tags: list[str] | None = None) -> int:
    tags = tags or generate_tags(content, "note")
    return save_item("note", content, tags)

def save_todo(content: str, tags: list[str] | None = None) -> int:
    tags = tags or generate_tags(content, "todo")
    return save_item("todo", content, tags)

def save_process(content: str, tags: list[str] | None = None) -> int:
    tags = tags or generate_tags(content, "process")
    return save_item("process", content, tags)

def save_protocol(content: str, tags: list[str] | None = None) -> int:
    tags = tags or generate_tags(content, "protocol")
    return save_item("protocol", content, tags)
```

- Ne JAMAIS mélanger les types (pas de `save_note` qui appelle `save_item("todo", ...)` ou autre incohérence).

---

### 1.3 Lecture filtrée uniquement par type dans `memory_core.py`

Objectif : régler le bug où un affichage de notes récupère aussi d’anciens contacts ou d’autres types.

- Toujours dans `memory_core.py`, localiser la fonction qui lit les items, par exemple :

```python
def get_items(item_type: str, limit: int = 50) -> list[dict]:
    ...
```

- S’assurer que la requête SQL filtre explicitement par `type` :

```python
cur.execute(
    """
    SELECT id, type, content, tags, extra, created_at
    FROM items
    WHERE type = ?
    ORDER BY created_at DESC
    LIMIT ?
    """,
    (item_type, limit),
)
```

- Tous les appels de `get_items` pour les notes doivent utiliser `item_type="note"`.

Vérifier dans `agents/orchestrator.py` que :
- l’action `memory_list_notes` appelle bien `get_items("note", ...)`,
- idem pour `todo`, `process`, `protocol`.

---

## 2️⃣ CONTACTS

Objectif : que les contacts soient **complètement sortis** de l’ancienne logique “note structurée” et passés UNIQUEMENT par `contacts.py`.

### 2.1 Vérifier le schéma SQL des contacts (optionnel)

- Ouvrir `memory/schema.sql`.
- Vérifier / ajouter une table `contacts` cohérente, par exemple :

```sql
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    aliases TEXT,         -- JSON list
    phones TEXT,          -- JSON list
    emails TEXT,          -- JSON list
    relationship TEXT,    -- JSON dict {category, role}
    notes TEXT,           -- JSON list
    whatsapp_number TEXT,
    tags TEXT,            -- JSON list
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Adapter aux noms de colonnes réellement utilisés si la table existe déjà.

---

### 2.2 Implémentation cohérente dans `memory/contacts.py`

Objectif : s’assurer que `contacts.py` fait exactement ce que l’orchestrator attend.

- Ouvrir `memory/contacts.py`.
- Vérifier / ajuster ces fonctions (ou créer si manquantes) :

```python
def save_contact(contact: dict) -> int:
    """
    contact = {
        "first_name": "...",
        "last_name": "...",
        "aliases": [...],
        "phones": [...],
        "emails": [...],
        "relationship": {"category": "...", "role": "..."},
        "notes": [...],
        "whatsapp_number": "...",
        "tags": [...],
    }
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO contacts (
                first_name, last_name, aliases, phones, emails,
                relationship, notes, whatsapp_number, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                contact.get("first_name"),
                contact.get("last_name"),
                json.dumps(contact.get("aliases", [])),
                json.dumps(contact.get("phones", [])),
                json.dumps(contact.get("emails", [])),
                json.dumps(contact.get("relationship", {})),
                json.dumps(contact.get("notes", [])),
                contact.get("whatsapp_number"),
                json.dumps(contact.get("tags", [])),
            ),
        )
        conn.commit()
        return cur.lastrowid


def update_contact(contact_id: int, updates: dict) -> None:
    # Construire dynamiquement le SET sur les champs concernés
    ...


def get_all_contacts(limit: int = 50) -> list[dict]:
    ...  # SELECT * FROM contacts ORDER BY created_at DESC LIMIT ?


def find_contacts(query: str, limit: int = 50) -> list[dict]:
    # Chercher sur first_name, last_name, aliases, emails, phones, etc.
    ...
```

- Aucune de ces fonctions ne doit écrire dans `items` ni dans `notes`.  
- Tout ce qui concerne les contacts doit passer par la table `contacts`.

---

### 2.3 Orchestrator : actions contacts correctement câblées

- Ouvrir `agents/orchestrator.py`.
- Dans `_process_memory_action(intent)`, vérifier :

```python
elif action == "save_contact":
    from memory.contacts import save_contact
    contact = intent.get("contact")
    contact_id = save_contact(contact)
    return f"✓ Contact sauvegardé (ID: {contact_id})"

elif action == "update_contact":
    from memory.contacts import update_contact
    contact_id = intent.get("contact_id")
    updates = intent.get("updates", {})
    update_contact(contact_id, updates)
    return f"✓ Contact mis à jour (ID: {contact_id})"

elif action == "list_contacts":
    from memory.contacts import get_all_contacts
    contacts = get_all_contacts(limit=50)
    # Option : formatter un résumé lisible pour l’utilisateur
    return format_contacts_summary(contacts)

elif action == "search_contacts":
    from memory.contacts import find_contacts
    query = intent.get("query", "")
    contacts = find_contacts(query=query, limit=50)
    return format_contacts_summary(contacts)
```

- S’assurer que **aucun** fallback ne renvoie vers des “notes structurées pour contact”.
- Vérifier que le prompt système (system prompt) décrit bien **exactement** ce format JSON attendu pour `memory_action: "save_contact"`.

---

## 3️⃣ PRÉFÉRENCES

Objectif : que les préférences ne soient plus juste “affichées”, mais réellement persistées.

### 3.1 Aligner le nom de l’action dans orchestrator + prompt

- Dans `agents/orchestrator.py`, vérifier que l’action attendue est bien `memory_action: "set_preference"` (ou `memory_set_preference`, mais il faut que ce soit le **même nom** partout).
- Dans le prompt système, s’assurer que l’exemple donné au LLM utilise exactement le même nom d’action que le code :

```json
{"memory_action": "set_preference",
 "preference": {"key": "language", "value": "fr"}}
```

Pas de variation type `"memory_set_preference"` d’un côté et `"set_preference"` de l’autre.

---

### 3.2 Implémentation dans `memory_core.py`

- Vérifier / corriger la fonction `save_preference` :

```python
def save_preference(key: str, value: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO preferences (key, value, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            (key, value),
        )
        conn.commit()
        return cur.lastrowid
```

Adapter aux colonnes réelles si la table `preferences` existe déjà.

- S’assurer que `_process_memory_action` appelle bien `save_preference` via un helper ou directement.

---

## 4️⃣ TAGGING AUTO (notes / todos)

Objectif : corriger le cas où “Je dois appeler ma femme” n’a généré aucun tag.

- Ouvrir `memory/tagging.py`.
- Vérifier que `generate_tags(content, item_type)` fonctionne de manière simple :
  - découpage grossier du texte,
  - filtrage de stop-words évidents,
  - éventuellement quelques heuristiques simples.

- Vérifier dans `helpers.py` que, **si aucun tag n’est fourni dans l’intent JSON**, on appelle **toujours** `generate_tags` :

```python
def save_todo(content: str, tags: list[str] | None = None) -> int:
    if not tags:
        tags = generate_tags(content, "todo")
    return save_item("todo", content, tags)
```

Même chose pour les notes.

On ne cherche pas à faire un tagging parfait maintenant → il faut juste que Clara **ne laisse plus un todo “nu” sans tags** par défaut.

---

## 5️⃣ RESET MÉMOIRE (nettoyage)

Objectif : repartir d’une base propre sans pollution de l’ancienne Clara.

### 5.1 Ajout d’une fonction `reset_memory()` dans `memory_core.py`

- Ajouter en bas de `memory_core.py` :

```python
def reset_memory(hard: bool = False) -> None:
    """
    Réinitialise la mémoire de Clara.
    Si hard=True, supprime aussi le fichier SQLite.
    """
    if hard:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        return

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        # À adapter aux tables réellement utilisées
        cur.execute("DELETE FROM items;")
        cur.execute("DELETE FROM preferences;")
        # Ajouter si nécessaire : contacts, etc. (si stockés aussi en SQL)
        conn.commit()
```

- **IMPORTANT** : adapter la liste des tables aux vraies tables en place (`contacts`, `events`, etc. si besoin).

### 5.2 Script ponctuel (une fois) ou appel manuel

Dans le patch, proposer à l’utilisateur (Jeremy) d’appeler une fois ce reset, par exemple via un petit script temporaire `scripts/reset_memory_once.py` ou via un appel Python rapide.

Ne pas l’appeler automatiquement au lancement de Clara → ce doit être une action volontaire.

---

## 6️⃣ JOURNALISATION

À la fin du patch, créer un fichier :

`journal/cursor_gpt/2025-12-05_patch_memory_contacts_cleanup.md`

Contenu minimal :

- Contexte (bugs notes, contacts, préférences non persistées, mélange de types)
- Fichiers modifiés
- Décisions clés (filtrage par type, séparation totale contacts / notes, alignement nom d’action set_preference, ajout reset_memory)
- Tests effectués (ex. : création de note, todo, process, protocole, préférence, contact + lecture)
- Résultat attendu.

Commit message proposé :

```text
Phase 2 – Fix memory pipeline (notes/todos/process/protocol/preferences/contacts) + reset helper
```

---

## 7️⃣ Tests à exécuter après patch

1. Créer une note :  
   > « Ajoute une note : demain appeler le plombier »  
   Puis :  
   > « Montre-moi toutes mes notes »  
   → La note doit apparaître, seule, sans contact mélangé.

2. Créer un todo :  
   > « Ajoute un todo : envoyer le contrat à David »  
   Puis :  
   > « Cherche les todos qui parlent de contrat »  
   → Le todo doit être trouvé.

3. Créer un process et un protocole, puis les lister → vérifier qu’ils ne se croisent pas.

4. Créer une préférence :  
   > « À partir de maintenant, je préfère que tu me répondes en français »  
   → Vérifier dans la DB que la préférence est stockée dans `preferences`.

5. Créer un contact complet :  
   > « Enregistre un contact : Aurélie Malai, ma femme, numéro 0500000000, email aurelie@example.com, alias Louloute »  
   → Vérifier que le contact est bien dans la table `contacts` et **n’apparaît plus du tout dans les notes**.

6. (Optionnel) Utiliser `reset_memory()` pour repartir à zéro et rejouer 1–5 pour confirmer la stabilité.

---

Fin du patch.
