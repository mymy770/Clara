# Phase 3 – Connexion Clara ↔ Mémoire
Date: 2025-12-05

## Contexte

Après la Phase 2 où nous avons créé l'infrastructure mémoire SQLite et l'API fonctionnelle, Clara dispose d'une mémoire persistante mais ne l'utilise pas encore. La Phase 3 connecte l'orchestrateur à cette mémoire de manière simple et explicite.

**État avant Phase 3 :**
- ✅ Base SQLite `memory/memory.sqlite` créée
- ✅ API mémoire fonctionnelle (save_item, get_items, search_items, delete_item)
- ✅ Schéma table `memory` avec types flexibles
- ❌ Clara ne peut pas encore utiliser sa mémoire

**Objectif Phase 3 :**
Permettre à Clara d'utiliser sa mémoire pour les notes via des commandes explicites de l'utilisateur, sans logique automatique complexe.

## Décisions

### 1. API Mémoire Générique

L'API existante dans `memory_core.py` est conservée telle quelle :
- `init_db()` : initialisation
- `save_item(type, content, tags)` : sauvegarde générique
- `get_items(type, limit)` : récupération avec filtres
- `search_items(query, type)` : recherche textuelle
- `update_item(item_id, content, tags)` : mise à jour
- `delete_item(item_id)` : suppression

Toutes utilisent le chemin unique : `memory/memory.sqlite`

### 2. Helpers Typés

Création de `memory/helpers.py` pour faciliter l'utilisation :

```python
save_note(content, tags)
save_process(content, tags)
save_protocol(content, tags)
save_todo(content, tags)
save_contact(content, tags)
```

Ces helpers appellent simplement `save_item()` avec le type approprié.

**Avantages :**
- Code plus lisible
- Type safety
- Facilite l'ajout de nouvelles fonctions spécialisées

### 3. Système d'Intentions JSON

**Pattern choisi : LLM retourne intentions + texte naturel**

Au lieu de faire du parsing complexe, on demande au LLM de retourner :
1. Une réponse textuelle naturelle pour l'utilisateur
2. Un bloc JSON d'intention (si action mémoire nécessaire)

**Format d'intention :**
```json
{"memory_action": "save_note", "content": "...", "tags": ["..."]}
```

**Actions supportées (Phase 3) :**
- `memory_save_note` : Sauvegarder une note
- `memory_list_notes` : Lister toutes les notes
- `memory_search_notes` : Chercher dans les notes
- `memory_delete_item` : Supprimer un élément par ID

### 4. Modification du Prompt Système

Le prompt système de Clara a été étendu pour inclure :
- Description des capacités mémoire
- Liste des actions disponibles
- Format JSON attendu pour les intentions
- Instructions claires sur le format de réponse

**Principe :** Le LLM doit toujours répondre naturellement ET inclure le JSON si nécessaire.

### 5. Limites de la Phase 3

**Ce qui est fait :**
- ✅ Commandes explicites pour les notes
- ✅ Parsing des intentions JSON
- ✅ Appels aux fonctions mémoire
- ✅ Retour de résultats à l'utilisateur

**Ce qui n'est PAS fait (volontairement) :**
- ❌ Détection automatique de ce qui doit être mémorisé
- ❌ Logique complexe d'extraction d'informations
- ❌ Support de tous les types (contacts, process, protocol)
- ❌ Intégration avec agents spécialisés

**Raison :** Établir d'abord une base simple et stable.

## Fichiers créés

### 1. `memory/helpers.py` (nouveau)
- 5 fonctions helper typées
- Wrappers simples autour de `save_item()`
- ~30 lignes de code

### 2. `tests/test_memory_core.py` (nouveau/complété)
- Tests unitaires complets pour l'API mémoire
- Test save, get, search, update, delete
- Utilise des DB temporaires
- ~120 lignes de code

## Fichiers modifiés

### 3. `agents/orchestrator.py` (modifié)

**Imports ajoutés :**
```python
import json
import re
from memory.helpers import save_note
from memory.memory_core import get_items, search_items, delete_item
```

**Nouvelles méthodes :**
- `_process_memory_action(response_text)` : Extrait et exécute intentions JSON
- `_clean_response(response_text)` : Nettoie la réponse du bloc JSON

**Prompt système étendu :**
- Section "Capacités mémoire (Phase 3)"
- Liste des actions disponibles
- Format JSON d'intention
- Instructions pour le LLM

**Logique dans `handle_message()` :**
1. Recevoir message utilisateur
2. Appeler LLM
3. Parser la réponse pour trouver une intention JSON
4. Si intention trouvée : exécuter l'action mémoire
5. Ajouter le résultat à la réponse
6. Nettoyer le JSON de la réponse finale
7. Retourner la réponse propre à l'utilisateur

**Gestion d'erreurs :**
- Si le JSON est invalide : ignorer silencieusement
- Si l'action échoue : ignorer silencieusement
- Clara continue de fonctionner normalement

## Implémentation technique

### Flux d'une commande mémoire

```
User: "Sauvegarde ceci en note : Clara Phase 3"
    ↓
Orchestrator → LLM (avec prompt étendu)
    ↓
LLM retourne:
    "D'accord, je sauvegarde cette note."
    ```json
    {"memory_action": "save_note", "content": "Clara Phase 3"}
    ```
    ↓
Orchestrator extrait JSON → save_note("Clara Phase 3")
    ↓
Retourne: item_id = 1
    ↓
Orchestrator nettoie réponse + ajoute résultat
    ↓
Clara: "D'accord, je sauvegarde cette note.

✓ Note sauvegardée (ID: 1)"
```

### Exemples de commandes supportées

**Sauvegarder une note :**
```
User: Sauvegarde ceci en note : Clara est géniale
Clara: ✓ Note sauvegardée (ID: 1)
```

**Lister les notes :**
```
User: Montre-moi toutes mes notes
Clara: 📝 1 note(s) trouvée(s) :
  - ID 1: Clara est géniale...
```

**Chercher dans les notes :**
```
User: Cherche dans mes notes le mot "Clara"
Clara: 🔍 1 note(s) trouvée(s) pour 'Clara' :
  - ID 1: Clara est géniale...
```

**Supprimer une note :**
```
User: Supprime la note avec l'id 1
Clara: ✓ Élément 1 supprimé
```

## Tests effectués

### Tests unitaires

```bash
python3 -m unittest tests.test_memory_core
```

**Résultats :**
- ✅ test_save_and_get_item
- ✅ test_search_items
- ✅ test_delete_item
- ✅ test_update_item

Tous les tests passent.

### Tests manuels (conversation)

```bash
python3 run_clara.py
```

**Scénarios testés :**

1. **Sauvegarde de note :**
   - Commande : "Sauvegarde en note : Test Phase 3"
   - Résultat : ✅ Note créée
   - Vérification DB : ✅ Présente dans memory.sqlite

2. **Liste des notes :**
   - Commande : "Montre mes notes"
   - Résultat : ✅ Liste affichée

3. **Recherche :**
   - Commande : "Cherche 'Phase 3' dans mes notes"
   - Résultat : ✅ Note trouvée

4. **Suppression :**
   - Commande : "Supprime la note 1"
   - Résultat : ✅ Note supprimée

5. **Conversation normale (sans mémoire) :**
   - Commande : "Bonjour, comment vas-tu ?"
   - Résultat : ✅ Réponse normale sans appel mémoire

**Conclusion des tests :** Tous les scénarios fonctionnent correctement.

## Architecture Phase 3 (finale)

```
Clara démarre
    ↓
init_db() → Crée memory/memory.sqlite
    ↓
Orchestrator initialise (avec prompt étendu)
    ↓
Boucle de conversation
    ↓
User message → Orchestrator
    ↓
LLM (prompt système avec capacités mémoire)
    ↓
Réponse + Intention JSON (optionnel)
    ↓
Parser intention → Exécuter action mémoire
    ↓
Nettoyer réponse + Ajouter résultat
    ↓
Response to user
    ↓
Logs (session + debug + actions mémoire)
```

## Prochaines étapes (Phase 4+)

### Extension des types

Actuellement seules les notes sont pleinement intégrées. Prochainement :
- `contact` : Gestion des contacts
- `todo` : Liste de tâches
- `process` : Processus/workflows
- `protocol` : Protocoles établis

### Détection automatique

Future phase : Clara pourra détecter automatiquement :
- Les contacts mentionnés
- Les tâches demandées
- Les préférences exprimées
- Les faits importants

Et les sauvegarder sans commande explicite.

### Agents spécialisés

Future intégration avec :
- Agent mémoire dédié
- Agents multi-tâches (AutoGen)
- Agents avec outils (filesystem, mail, etc.)

### Mémoire vectorielle

Future extension pour recherche sémantique :
- Embeddings des notes
- Recherche par similarité
- Clustering des informations

## Limitations connues

### 1. Dépendance au LLM

Si le LLM ne retourne pas le JSON correctement, l'action n'est pas exécutée.

**Mitigation :** 
- Prompt clair et précis
- Gestion d'erreur silencieuse (Clara continue de fonctionner)
- Tests manuels pour valider le comportement

### 2. Pas de contexte long terme

L'historique de conversation est en RAM uniquement. Clara ne "se souvient" pas des sessions précédentes automatiquement.

**Mitigation future :**
- Charger le contexte pertinent depuis SQLite
- Résumés de sessions
- Mémoire contextuelle

### 3. Actions limitées

Seulement 4 actions mémoire pour l'instant.

**Mitigation :** Extension progressive en Phase 4+.

## Conclusion

**Phase 3 : Connexion Clara ↔ Mémoire ✅ TERMINÉE**

Clara peut maintenant :
- ✅ Sauvegarder des notes
- ✅ Lister ses notes
- ✅ Chercher dans ses notes
- ✅ Supprimer des notes
- ✅ Converser normalement

L'architecture est :
- ✅ Simple et maintenable
- ✅ Extensible (nouveaux types faciles à ajouter)
- ✅ Testée (tests unitaires + manuels)
- ✅ Documentée

**Clara a maintenant une mémoire fonctionnelle ! 🧠💾**

La base est établie pour des fonctionnalités plus avancées en Phase 4+.

