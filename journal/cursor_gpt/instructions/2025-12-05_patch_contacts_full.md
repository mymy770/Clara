2025-12-05 — Patch Contacts & Intégration Orchestrator → Cursor

🎯 Objectif

Corriger entièrement l’intégration du module “contacts” qui n’a jamais été connecté à Clara (orchestrator, prompt, memory actions, intents, helpers…).

⸻

1️⃣ Modification : system_prompt (orchestrator.py)

Ajouter un bloc CONTACTS complet dans _build_system_prompt() :

➤ À insérer AVANT les blocs NOTES/TODOS :
CONTACTS :
- memory_save_contact : enregistrer un contact structuré
- memory_update_contact : modifier un contact existant
- memory_list_contacts : lister tous les contacts
- memory_search_contacts : rechercher dans les contacts

Format JSON attendu :

```json
{"memory_action": "save_contact",
 "contact": {
    "prenom": "...",
    "nom": "...",
    "alias": ["..."],
    "phones": [{"number": "...", "channel": "mobile", "primary": true}],
    "emails": [{"email": "...", "label": "perso", "primary": true}],
    "relationship": {"category": "family", "role": "wife"},
    "notes": ["..."],
    "whatsapp_number": "...",
    "tags": ["contact"]
  }}
Ajouter aussi les variantes :
{“memory_action”: “list_contacts”}
{“memory_action”: “search_contacts”, “query”: “…”}
{“memory_action”: “update_contact”, “contact_id”: 12, “updates”: {…}}
---

# 2️⃣ **Modification : orchestrator._process_memory_action()**  
Ajouter les 4 nouveaux cas :
elif action == “save_contact”:
from contacts import save_contact
contact = intent.get(“contact”)
item_id = save_contact(contact)
return f”✓ Contact sauvegardé (ID: {item_id})”

elif action == “update_contact”:
from contacts import update_contact
contact_id = intent.get(“contact_id”)
updates = intent.get(“updates”)
update_contact(contact_id, updates)
return f”✓ Contact mis à jour (ID: {contact_id})”

elif action == “list_contacts”:
from contacts import list_contacts
contacts = list_contacts()
return f”{len(contacts)} contact(s) trouvé(s)”

elif action == “search_contacts”:
from contacts import search_contacts
query = intent.get(“query”)
results = search_contacts(query)
return f”{len(results)} résultat(s) pour ‘{query}’”
---

# 3️⃣ **Modification : orchestrator._check_memory_read_intent()**  
Ajouter la détection de lecture CONTACTS :
if “contact” in msg_lower or “numéro” in msg_lower or “email” in msg_lower:
contacts = list_contacts(limit=20)
return f”CONTACTS: {len(contacts)} enregistrés”
---

# 4️⃣ **helpers.py**
Créer les helpers manquants :
def save_contact(contact_dict):
return create_item(type=“contact”, content=json.dumps(contact_dict), tags=[“contact”])

def update_contact(contact_id, updates):
return update_item(contact_id, updates)

def list_contacts(limit=50):
return get_items(type=“contact”, limit=limit)

def search_contacts(query, limit=50):
return search_items(query=query, type=“contact”, limit=limit)
---

# 5️⃣ **memory_core.py**
Créer la table contact :
CREATE TABLE IF NOT EXISTS contacts (
id INTEGER PRIMARY KEY AUTOINCREMENT,
prenom TEXT,
nom TEXT,
alias TEXT,
phones TEXT,
emails TEXT,
relationship TEXT,
notes TEXT,
whatsapp_number TEXT,
tags TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Créer les fonctions CRUD correspondantes si elles n’existent pas.

---

# 6️⃣ **tagging.py**  
Ajouter des tags automatiques pour contacts :
def auto_tags_for_contact(contact_dict):
tags = [“contact”]
if “relationship” in contact_dict:
tags.append(contact_dict[“relationship”].get(“category”))
tags.append(contact_dict[“relationship”].get(“role”))
return tags

def auto_tags_for_contact(contact_dict):
tags = [“contact”]
if “relationship” in contact_dict:
tags.append(contact_dict[“relationship”].get(“category”))
tags.append(contact_dict[“relationship”].get(“role”))
return tags

---

# 7️⃣ **Test à réaliser après patch**
1. `"Ajoute le contact : Aurélie Malai, ma femme, number..., email..."`  
   → Doit créer un contact structuré

2. `"Montre tous mes contacts"`  
   → Doit utiliser list_contacts()

3. `"Trouve mon contact : Aurélie"`  
   → Doit utiliser search_contacts()

4. `"Mets à jour son numéro WhatsApp"`  
   → Doit utiliser update_contact()

---

# 8️⃣ **Notes pour journalisation**
Après modification, merci d’archiver :

- Fichier original
- Fichier modifié
- Résultat des tests
- Commit message :  
  **"Phase 2 — Full contact integration (prompt + orchestrator + memory + helpers)"**

---

# 📌 Fin du patch

---

Tout est prêt.  
Tu peux maintenant envoyer le fichier à Cursor.