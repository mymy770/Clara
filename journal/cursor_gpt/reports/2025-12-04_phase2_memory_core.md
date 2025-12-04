# Phase 2 – Memory Core
Date: 2025-12-04

## Contexte

Suite à la Phase 1 où Clara a acquis sa capacité conversationnelle de base, nous devons maintenant lui donner une mémoire persistante et structurée. Cette Phase 2 crée l'infrastructure de stockage mémoire, sans encore y connecter de logique métier ou d'intelligence.

**Ce qui existait déjà :**
- Une petite table SQLite `interactions` pour l'historique de conversation
- Pas de système de mémoire polyvalent
- Pas d'API pour stocker différents types d'informations

**Objectif Phase 2 :**
Créer une API mémoire simple et réutilisable pour stocker différents types d'items (contacts, tâches, préférences, protocoles, etc.) sans logique métier.

## Décisions

### 1. Schéma de base de données

**Choix : Table unique polyvalente `memory`**

Plutôt que de créer une table par type (contacts, tasks, etc.), nous avons opté pour une table générique avec un champ `type` flexible.

**Avantages :**
- Simplicité : une seule table à gérer
- Flexibilité : ajout de nouveaux types sans migration
- Uniformité : même API pour tous les types
- Évolutivité : tags JSON pour métadonnées additionnelles

**Structure :**
```sql
memory (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT (JSON),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Index :**
- `idx_memory_type` : pour filtrer par type rapidement
- `idx_memory_created_at` : pour trier chronologiquement

### 2. API Python

**Choix : Fonctions pures plutôt que classe**

L'API est composée de 6 fonctions indépendantes :
1. `init_db()` : initialisation
2. `save_item()` : création
3. `update_item()` : mise à jour
4. `get_items()` : récupération avec filtres
5. `search_items()` : recherche textuelle
6. `delete_item()` : suppression

**Avantages :**
- Simplicité d'utilisation
- Pas d'état à gérer
- Facilement testable
- Context managers pour sécurité des connexions

**Contraintes respectées :**
- Utilisation de `sqlite3` (stdlib)
- JSON pour sérialisation des tags
- Context managers (`with`) partout
- `row_factory` pour colonnes nommées
- AUCUNE logique métier

## Changements effectués

### Fichiers créés

1. **`memory/schema.sql`** (nouveau)
   - Définition de la table `memory`
   - Index pour performances
   - Commentaires explicatifs

2. **`memory/memory_core.py`** (remplacé/créé)
   - 6 fonctions d'API complètes
   - ~230 lignes de code propre
   - Documentation complète
   - Gestion d'erreurs implicite (context managers)

### Fichiers modifiés

3. **`run_clara.py`**
   - Import de `init_db`
   - Appel de `init_db()` au démarrage
   - Message de confirmation "Mémoire initialisée"

### Structure

```
memory/
├── schema.sql          # Définition SQL ✅
├── memory_core.py      # API Python ✅
└── memory.sqlite       # Base de données (créée au runtime)
```

## Implémentation technique

### Types d'items supportés (exemples)

Le système est prévu pour supporter (sans logique spéciale) :
- `contact` : informations de contact
- `task` : tâches à faire
- `todo` : items de todo list
- `preference` : préférences utilisateur
- `process` : processus/workflows
- `protocol` : protocoles établis
- `note` : notes libres
- `project` : projets
- `fact` : faits appris

### Fonctionnalités de l'API

**Création :**
```python
item_id = save_item(
    type="contact",
    content="Jean Dupont, jean@example.com",
    tags=["work", "important"]
)
```

**Récupération :**
```python
# Tous les contacts
contacts = get_items(type="contact")

# Les 10 derniers items
recent = get_items(limit=10)
```

**Recherche :**
```python
# Recherche dans le contenu
results = search_items(query="jean", type="contact")
```

**Mise à jour :**
```python
update_item(item_id, content="Nouveau contenu")
update_item(item_id, tags=["nouveau", "tag"])
```

**Suppression :**
```python
delete_item(item_id)
```

## Tests manuels effectués

✅ Clara démarre et initialise la mémoire
✅ Fichier `memory.sqlite` créé automatiquement
✅ Table `memory` créée avec le bon schéma
✅ Pas d'erreur au démarrage

**Note :** L'API mémoire n'est pas encore utilisée dans le flux conversationnel (Phase 3).

## Prochaines étapes (Phase 3)

La mémoire est maintenant prête à être utilisée. Les prochaines phases pourront :

1. **Connecter l'orchestrateur à la mémoire**
   - Sauvegarder automatiquement les informations importantes
   - Rappeler le contexte des sessions précédentes
   - Apprendre les préférences utilisateur

2. **Ajouter des agents mémoire**
   - Agent pour gérer les contacts
   - Agent pour gérer les tâches/todos
   - Agent pour gérer les préférences

3. **Intelligence sur la mémoire**
   - Analyse du contenu pour extraction d'informations
   - Classification automatique des types
   - Suggestions basées sur l'historique

4. **UI Admin**
   - Visualisation de la mémoire
   - Édition manuelle des items
   - Export/import de données

## Conclusion

**Phase 2 : Memory Core ✅ TERMINÉE**

Clara dispose maintenant d'une mémoire persistante et flexible. Le système est :
- ✅ Simple et propre
- ✅ Polyvalent et extensible
- ✅ Sans logique métier (phase 3)
- ✅ Prêt pour l'intégration

Le fichier SQLite `memory.sqlite` sera créé automatiquement au premier lancement de Clara après cette mise à jour.

🧠 **Clara a maintenant une mémoire !**

