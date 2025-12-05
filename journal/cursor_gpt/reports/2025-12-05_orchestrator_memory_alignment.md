# Fix – Alignement Orchestrator avec Memory Core
Date: 2025-12-05

## Contexte

Après la Phase 2 où nous avons créé l'API mémoire sous forme de fonctions (`init_db()`, `save_item()`, etc.), l'orchestrator essayait toujours d'utiliser une ancienne classe `MemoryCore` qui n'existe plus.

**Erreur rencontrée :**
```
ImportError: cannot import name 'MemoryCore' from 'memory.memory_core'
```

**Cause :**
- Phase 1 : `memory_core.py` contenait une classe `MemoryCore`
- Phase 2 : Réécriture complète avec des fonctions pures (API fonctionnelle)
- Orchestrator : Toujours configuré pour utiliser l'ancienne classe

**Impact :**
Clara ne pouvait plus démarrer.

## Décisions

### 1. Suppression de l'intégration mémoire dans l'orchestrator

**Phase 2 = Infrastructure mémoire uniquement**

L'orchestrator ne doit PAS encore utiliser la mémoire. Son rôle actuel :
1. Recevoir le message utilisateur
2. Appeler le LLM
3. Renvoyer la réponse
4. Maintenir l'historique en RAM

La connexion à la mémoire SQLite sera faite en Phase 3.

### 2. Confirmation du fichier SQLite officiel

Fichier unique et officiel : `memory/memory.sqlite`

Toutes les fonctions de `memory_core.py` utilisent ce chemin par défaut.

### 3. Initialisation mémoire au démarrage uniquement

`run_clara.py` appelle `init_db()` au démarrage pour :
- Créer le dossier `memory/` si nécessaire
- Créer le fichier `memory.sqlite` 
- Appliquer le schéma SQL

Mais aucune sauvegarde n'est faite pendant les conversations (Phase 3).

## Fichiers modifiés

### 1. `agents/orchestrator.py`

**Suppressions :**
- Import : `from memory.memory_core import MemoryCore`
- Initialisation : `self.memory = MemoryCore(...)`
- Appel : `self.memory.save_interaction(...)`
- Méthode : `load_session_context(...)`

**Ajouts :**
- Commentaire explicatif : "Note: Sauvegarde mémoire sera ajoutée en Phase 3"
- Commentaire : "Historique en RAM uniquement pour Phase 2"

**Résultat :**
L'orchestrator est maintenant plus simple et focalisé sur son rôle actuel : orchestrer la conversation sans persistance.

### 2. `memory/memory_core.py`

**Vérifications effectuées :**
- ✅ Toutes les fonctions utilisent `db_path: str = "memory/memory.sqlite"` par défaut
- ✅ Aucune référence à `clara_memory.db`
- ✅ `init_db()` crée bien le dossier et applique le schéma
- ✅ Structure de la table `memory` inchangée

Aucune modification nécessaire.

### 3. `run_clara.py`

**Vérifications effectuées :**
- ✅ Import présent : `from memory.memory_core import init_db`
- ✅ Appel au démarrage : `init_db()` avant la boucle
- ✅ Message de confirmation : "✓ Mémoire initialisée"

Aucune modification nécessaire.

## Tests effectués

### Test de démarrage

```bash
python3 run_clara.py
```

**Résultat :**
- ✅ Aucune erreur d'import
- ✅ Fichier `memory/memory.sqlite` créé automatiquement
- ✅ Clara répond aux messages
- ✅ Historique de conversation maintenu (en RAM)
- ✅ Logs créés correctement

### Test de conversation

```
Vous: bonjour
Clara: Bonjour ! Comment puis-je vous aider aujourd'hui ?

Vous: comment tu t'appelles ?
Clara: Je m'appelle Clara. Je suis une assistante IA...

Vous: quit
```

✅ Tout fonctionne sans erreur.

## Architecture Phase 2 (finale)

```
Clara démarre
    ↓
init_db()  → Crée memory/memory.sqlite (si nécessaire)
    ↓
Orchestrator initialise
    ↓
Boucle de conversation
    ↓
User message → Orchestrator → LLM → Response
    ↓
Historique en RAM (pas de SQLite pour l'instant)
    ↓
Logs créés (session + debug)
```

**Mémoire SQLite :**
- Fichier créé : `memory/memory.sqlite` ✅
- Table `memory` prête : ✅
- API disponible : `save_item()`, `get_items()`, `search_items()`, etc. ✅
- **Utilisée par Clara : ❌ (Phase 3)**

## Prochaines étapes (Phase 3)

Phase 3 connectera l'orchestrator à la mémoire via l'API fonctionnelle :

1. **Sauvegarder automatiquement :**
   - Contacts mentionnés dans la conversation
   - Préférences apprises
   - Tâches demandées
   - Faits importants

2. **Rappeler le contexte :**
   - Informations des sessions précédentes
   - Préférences utilisateur
   - Historique long terme

3. **Intelligence sur la mémoire :**
   - Extraction d'informations depuis les messages
   - Classification automatique des types
   - Suggestions basées sur l'historique

## Conclusion

**Fix Orchestrator-Memory Alignment ✅ TERMINÉ**

L'orchestrator est maintenant aligné avec la nouvelle architecture Memory Core :
- ✅ Pas d'import de classe inexistante
- ✅ Pas d'appel à des méthodes obsolètes
- ✅ Clara démarre et fonctionne correctement
- ✅ Fichier SQLite unique : `memory/memory.sqlite`
- ✅ API mémoire prête pour Phase 3

**Phase 2 complètement stabilisée ! 🎯**




