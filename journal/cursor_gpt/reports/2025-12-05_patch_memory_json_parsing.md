# Patch : Fiabiliser l'écriture des notes (parsing JSON mémoire)
Date: 2025-12-05

## Contexte

**Problème identifié :**
Clara affichait parfois le bloc JSON de mémoire (`{"memory_action": ...}`) **sans** exécuter l'action (ex: `save_note`), parce que le LLM ne renvoyait pas exactement un bloc ```json ... ``` comme attendu.

**Causes :**
- Le parsing était trop strict : cherchait uniquement ````json { ... } ````
- Si le LLM renvoyait juste ```` { ... } ``` (sans `json`) ou un JSON nu, l'action n'était jamais exécutée
- Le JSON brut était affiché à l'utilisateur même après exécution de l'action

**Objectif :** Rendre le parsing plus robuste et tolérant aux variantes de format.

## Fichier modifié

### `agents/orchestrator.py`

#### 1. Détection JSON tolérante (`_process_memory_action()`)

**Avant :**
```python
json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
if not json_match:
    return None
```

**Problème :** Ne matchait que ````json { ... } ````

**Après :** Détection en cascade avec 3 niveaux de tolérance

```python
# 1) Essayer d'abord le cas idéal : ```json { ... } ```
json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)

# 2) Si rien trouvé, accepter n'importe quel bloc ``` { ... } ```
if not json_match:
    json_match = re.search(r"```\s*(\{.*?\})\s*```", response_text, re.DOTALL)

raw_json = None
fallback_match = None

# 3) Si on a trouvé un bloc code, on récupère le JSON
if json_match:
    raw_json = json_match.group(1)
else:
    # 4) Fallback : chercher un objet JSON "nu" dans le texte
    fallback_match = re.search(r"(\{\s*\"memory_action\".*?\})", response_text, re.DOTALL)
    if fallback_match:
        raw_json = fallback_match.group(1)

# Si on n'a toujours rien, on abandonne proprement
if not raw_json:
    return (response_text, None)
```

**Formats acceptés maintenant :**
1. ````json { ... } ``` (format idéal)
2. ```` { ... } ``` (bloc code sans spécificateur de langue)
3. `{ "memory_action": ... }` (JSON nu dans le texte)

#### 2. Nettoyage de la réponse utilisateur

**Avant :** Le JSON brut restait dans la réponse même après exécution

**Après :** Nettoyage automatique après exécution de l'action

```python
# Nettoyage : on retire le bloc JSON de la réponse utilisateur
try:
    if json_match:
        cleaned = response_text.replace(json_match.group(0), "").strip()
    else:
        # Fallback : si on a utilisé fallback_match, on enlève juste le JSON nu
        if fallback_match:
            cleaned = response_text.replace(fallback_match.group(1), "").strip()
        else:
            cleaned = response_text
except Exception:
    cleaned = response_text

return (cleaned or "C'est enregistré.", result_message)
```

**Résultat :** L'utilisateur ne voit plus le JSON brut, seulement la réponse naturelle de Clara + le message de confirmation.

#### 3. Changement de signature de fonction

**Avant :**
```python
def _process_memory_action(self, response_text):
    ...
    return result_message  # ou None
```

**Après :**
```python
def _process_memory_action(self, response_text):
    ...
    return (cleaned_response, result_message)  # ou (response_text, None)
```

**Raison :** Permet de retourner à la fois la réponse nettoyée (sans JSON) et le message de résultat.

#### 4. Adaptation de l'appelant

**Avant :**
```python
memory_result = self._process_memory_action(clara_response)
if memory_result:
    clara_response = self._clean_response(clara_response) + f"\n\n{memory_result}"
```

**Après :**
```python
cleaned_response, memory_result = self._process_memory_action(clara_response)
if memory_result:
    clara_response = cleaned_response + f"\n\n{memory_result}"
else:
    clara_response = cleaned_response
```

**Raison :** Utilise la réponse nettoyée retournée par `_process_memory_action` au lieu de nettoyer manuellement.

#### 5. Refactorisation des actions

**Changement :** Toutes les actions stockent maintenant le message dans `result_message` au lieu de `return` immédiatement.

**Avant :**
```python
if action == 'save_note':
    ...
    return f"✓ Note sauvegardée (ID: {item_id})"
```

**Après :**
```python
if action == 'save_note':
    ...
    result_message = f"✓ Note sauvegardée (ID: {item_id})"
```

**Raison :** Permet de nettoyer la réponse et de retourner le tuple à la fin de la fonction.

#### 6. Logging optionnel

**Ajout :** Log pour diagnostiquer l'exécution des actions mémoire

```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"memory_action_executed: action={action}, raw_json={raw_json[:100] if len(raw_json) > 100 else raw_json}...")
```

**Utilité :** Permet de vérifier dans les logs que :
- Le JSON est bien détecté
- L'action est exécutée
- On ne dépend plus du strict ````json`

## Décisions techniques

### 1. Détection en cascade vs Regex unique

**Choix :** Détection en cascade (3 niveaux)

**Raisons :**
- Plus robuste : accepte plusieurs formats
- Plus lisible : chaque niveau est clair
- Plus maintenable : facile d'ajouter d'autres formats

### 2. Tuple de retour vs Modification in-place

**Choix :** Retourner un tuple `(cleaned_response, result_message)`

**Raisons :**
- Fonction pure : ne modifie pas l'entrée
- Plus testable : retour explicite
- Plus flexible : permet de gérer les deux valeurs séparément

### 3. Nettoyage automatique vs Optionnel

**Choix :** Nettoyage automatique après exécution

**Raisons :**
- Meilleure UX : l'utilisateur ne voit jamais le JSON brut
- Cohérent : toutes les actions mémoire sont nettoyées de la même manière
- Simple : pas besoin de configuration

## Tests effectués

### 1. Format idéal (```json)
```
"Sauvegarde une note : demain appeler le plombier"
→ LLM renvoie : ```json {"memory_action": "save_note", ...} ```
→ Action exécutée ✅
→ JSON retiré de la réponse ✅
```

### 2. Format sans spécificateur (```)
```
"Sauvegarde une note : demain appeler le plombier"
→ LLM renvoie : ``` {"memory_action": "save_note", ...} ```
→ Action exécutée ✅
→ JSON retiré de la réponse ✅
```

### 3. Format JSON nu
```
"Sauvegarde une note : demain appeler le plombier"
→ LLM renvoie : {"memory_action": "save_note", ...}
→ Action exécutée ✅
→ JSON retiré de la réponse ✅
```

### 4. Liste des notes
```
"Montre-moi toutes mes notes"
→ Action exécutée ✅
→ Notes affichées correctement ✅
```

## Résultat attendu

✅ **Le parsing JSON est tolérant aux variantes de format**  
✅ **Les actions mémoire sont toujours exécutées si un JSON valide est détecté**  
✅ **Le JSON brut n'est plus affiché à l'utilisateur**  
✅ **Les logs permettent de diagnostiquer facilement les exécutions**

## Instructions non traitées

**Aucune.** Toutes les instructions ont été implémentées :
- ✅ Détection JSON tolérante (3 niveaux)
- ✅ Nettoyage de la réponse utilisateur
- ✅ Logging optionnel
- ✅ Refactorisation complète de la fonction

## Prochaines étapes

### Utilisation

Le patch est transparent pour l'utilisateur. Clara fonctionne maintenant même si le LLM :
- Oublie le spécificateur `json` dans le bloc code
- Utilise un bloc code sans spécificateur
- Renvoie un JSON nu dans le texte

### Améliorations possibles

1. **Validation JSON :** Vérifier que le JSON contient bien `memory_action` avant de parser
2. **Détection multiple :** Gérer le cas où plusieurs blocs JSON sont présents
3. **Format alternatifs :** Accepter d'autres formats (YAML, etc.)

## Conclusion

**Patch JSON Parsing : TERMINÉ ✅**

Le parsing JSON est maintenant :
- ✅ **Robuste** : Accepte 3 formats différents
- ✅ **Tolérant** : Ne dépend plus du format exact
- ✅ **Propre** : N'affiche plus le JSON brut
- ✅ **Traçable** : Logs pour diagnostic

**Aucun impact sur les fonctionnalités existantes** (toutes les actions mémoire continuent de fonctionner normalement). 🎯✨📝

