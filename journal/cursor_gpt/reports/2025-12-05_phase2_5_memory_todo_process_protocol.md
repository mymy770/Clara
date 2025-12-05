# Phase 2.5 – Extension Mémoire : TODO / PROCESS / PROTOCOL
Date: 2025-12-05

## Contexte

Suite à la Phase 3 où Clara a acquis la capacité de gérer des notes en mémoire, cette Phase 2.5 étend ces capacités à trois nouveaux types :
- **todo** : Choses à faire, tâches
- **process** : Procédures détaillées, workflows
- **protocol** : Protocoles, règles générales

**État avant Phase 2.5 :**
- ✅ Mémoire SQLite fonctionnelle
- ✅ API générique (save_item, get_items, search_items, delete_item)
- ✅ Notes supportées avec intentions JSON
- ❌ Autres types non exposés à l'orchestrator

**Objectif Phase 2.5 :**
Étendre le système d'intentions JSON pour supporter todo/process/protocol en réutilisant exactement le même pattern que pour les notes.

## Décisions

### 1. Réutilisation de l'architecture existante

**Aucun changement structurel**

L'API mémoire est déjà générique et supporte tous les types. Nous n'avons qu'à :
- Utiliser les helpers déjà créés (save_todo, save_process, save_protocol)
- Étendre le prompt système du LLM
- Étendre le parsing des intentions dans l'orchestrator

### 2. Helpers déjà présents

Les helpers existaient déjà dans `memory/helpers.py` depuis la Phase 3 :
- `save_todo()`
- `save_process()`
- `save_protocol()`

Ils n'ont pas besoin d'être modifiés, juste d'être importés et utilisés.

### 3. Extension du prompt système

Le prompt système a été étendu pour :
- Décrire les 3 nouveaux types (todo, process, protocol)
- Expliquer quand utiliser chaque type :
  - Todo : chose à faire
  - Process : procédure détaillée étape par étape
  - Protocol : règle générale ou principe à respecter
- Lister les nouvelles actions disponibles

### 4. Extension du parsing d'intentions

Le code de `_process_memory_action()` a été étendu avec :
- `save_todo` → appelle save_todo()
- `list_todos` → appelle get_items(type='todo')
- `search_todos` → appelle search_items(type='todo')
- `save_process` → appelle save_process()
- `list_processes` → appelle get_items(type='process')
- `save_protocol` → appelle save_protocol()
- `list_protocols` → appelle get_items(type='protocol')

**Pattern identique aux notes :**
- Parsing du JSON
- Appel à la fonction appropriée
- Formatage du résultat
- Gestion d'erreur silencieuse

### 5. Limites de Phase 2.5

**Ce qui est fait :**
- ✅ 4 types supportés : note, todo, process, protocol
- ✅ Actions : save, list, search (notes/todos), delete (tous types)
- ✅ Format JSON cohérent
- ✅ Helpers typés

**Ce qui n'est PAS fait (volontairement) :**
- ❌ Contacts (Phase ultérieure)
- ❌ Détection automatique
- ❌ Logique d'extraction intelligente
- ❌ Relations entre items
- ❌ Validation de contenu

## Fichiers modifiés

### 1. `agents/orchestrator.py`

**Imports ajoutés :**
```python
from memory.helpers import save_note, save_todo, save_process, save_protocol
```

**Prompt système étendu :**
- Section NOTES (inchangée)
- Section TODOS (nouvelle)
- Section PROCESS (nouvelle)
- Section PROTOCOL (nouvelle)
- Exemples JSON pour chaque type
- Mise à jour version : "Phase 2.5"

**Méthode `_process_memory_action()` étendue :**
- 6 nouveaux cas traités :
  - save_todo
  - list_todos
  - search_todos
  - save_process
  - list_processes
  - save_protocol
  - list_protocols

**Formatage des résultats :**
- Todos : ✅ emoji
- Process : ⚙️ emoji
- Protocol : 📋 emoji
- Limite d'affichage : 10 items max

### 2. `tests/test_memory_helpers.py` (nouveau)

Tests unitaires complets pour les helpers :
- `test_save_todo()` : Sauvegarde et vérification
- `test_save_process()` : Sauvegarde et vérification
- `test_save_protocol()` : Sauvegarde et vérification
- `test_multiple_types_coexist()` : Coexistence de 4 types différents

~120 lignes de code de tests

### 3. `memory/helpers.py`

Aucune modification nécessaire - les fonctions existaient déjà.

## Tests effectués

### Tests unitaires

```bash
python3 -m unittest tests.test_memory_helpers
```

**Résultats :**
- ✅ test_save_todo
- ✅ test_save_process
- ✅ test_save_protocol
- ✅ test_multiple_types_coexist

Tous les tests passent.

### Tests manuels (conversation)

```bash
python3 run_clara.py
```

**Scénarios testés :**

1. **Todos :**
   ```
   User: Ajoute un todo : Appeler le fournisseur demain matin
   Clara: ✓ Todo sauvegardé (ID: X)
   
   User: Montre mes todos
   Clara: ✅ 1 todo(s) trouvé(s) : ...
   ```

2. **Process :**
   ```
   User: Sauvegarde ce processus : Pour vérifier un fournisseur : 1) Email 2) Historique
   Clara: ✓ Processus sauvegardé (ID: X)
   
   User: Liste mes processus
   Clara: ⚙️ 1 processus trouvé(s) : ...
   ```

3. **Protocol :**
   ```
   User: Sauvegarde ce protocole : Toujours être courtois dans les mails fournisseurs
   Clara: ✓ Protocole sauvegardé (ID: X)
   
   User: Montre mes protocoles
   Clara: 📋 1 protocole(s) trouvé(s) : ...
   ```

4. **Coexistence :**
   - Base SQLite contient maintenant notes + todos + process + protocols
   - Chaque type est filtrable indépendamment
   - Pas de conflit ni de perte de données

**Résultat :** Tous les scénarios fonctionnent correctement.

## Architecture Phase 2.5 (finale)

```
Table memory (SQLite)
├── type = "note"       ✅
├── type = "todo"       ✅ (nouveau)
├── type = "process"    ✅ (nouveau)
└── type = "protocol"   ✅ (nouveau)

API Memory Core (générique)
├── save_item()
├── get_items()
├── search_items()
├── update_item()
└── delete_item()

Helpers (typés)
├── save_note()
├── save_todo()         ✅ (utilisé)
├── save_process()      ✅ (utilisé)
└── save_protocol()     ✅ (utilisé)

Orchestrator (intentions)
├── memory_save_note
├── memory_list_notes
├── memory_search_notes
├── memory_save_todo       ✅ (nouveau)
├── memory_list_todos      ✅ (nouveau)
├── memory_search_todos    ✅ (nouveau)
├── memory_save_process    ✅ (nouveau)
├── memory_list_processes  ✅ (nouveau)
├── memory_save_protocol   ✅ (nouveau)
└── memory_list_protocols  ✅ (nouveau)
```

## Exemples d'utilisation

### Todo
```
User: Ajoute à ma liste : acheter du lait
Clara: [JSON intention: save_todo]
      ✓ Todo sauvegardé (ID: 5)
```

### Process
```
User: Enregistre cette procédure : Avant d'envoyer un mail client : 1) Relire 2) Vérifier pièces jointes 3) Vérifier destinataire
Clara: [JSON intention: save_process]
      ✓ Processus sauvegardé (ID: 6)
```

### Protocol
```
User: Note ce protocole : Toujours répondre aux mails dans les 24h
Clara: [JSON intention: save_protocol]
      ✓ Protocole sauvegardé (ID: 7)
```

## Prochaines étapes (Phase 4+)

### Contacts structurés

Les contacts nécessiteront probablement :
- Champs structurés (nom, email, téléphone, relation)
- Peut-être une table séparée
- Ou un format JSON dans le champ `content`

### Détection automatique

Clara pourra progressivement :
- Détecter automatiquement les todos dans la conversation
- Extraire les processus décrits par l'utilisateur
- Identifier les protocoles établis

### Relations entre items

Future extension :
- Lier des todos à des projets
- Associer des processus à des protocoles
- Créer des hiérarchies

### Agents spécialisés

Future intégration :
- Agent Todo Manager
- Agent Process Manager
- Agent Protocol Keeper
- Orchestration multi-agents (AutoGen)

## Conclusion

**Phase 2.5 : Extension Mémoire ✅ TERMINÉE**

Clara peut maintenant gérer :
- ✅ Notes (Phase 3)
- ✅ Todos (Phase 2.5)
- ✅ Processus (Phase 2.5)
- ✅ Protocoles (Phase 2.5)

Le système est :
- ✅ Cohérent (même pattern partout)
- ✅ Extensible (facile d'ajouter de nouveaux types)
- ✅ Testé (tests unitaires + manuels)
- ✅ Documenté (journal complet)

**Clara a maintenant une mémoire polyvalente ! 🧠📝✅⚙️📋**

Base solide établie pour Phase 4 et au-delà.

