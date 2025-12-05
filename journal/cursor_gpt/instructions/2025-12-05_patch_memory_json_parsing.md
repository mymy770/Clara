# Patch : Fiabiliser l’écriture des notes (parsing JSON mémoire)

## Objectif

Corriger le cas où Clara affiche le bloc JSON de mémoire (`{"memory_action": ...}`) **sans** exécuter l’action (ex : `save_note`), parce que le LLM ne renvoie pas exactement un bloc ```json … ``` comme attendu.

On rend le parsing plus robuste dans `agents/orchestrator.py` :
- on tolère plusieurs formats de bloc code,
- on exécute l’action mémoire même si le LLM oublie `json`,
- on évite d’afficher le bloc JSON brut à l’utilisateur.

---

## 1. Fichier à modifier

- `agents/orchestrator.py`

> Ne rien changer d’autre (memory_core, helpers, contacts, schema, etc. sont OK).

---

## 2. Renforcer `_process_memory_action`

Dans `agents/orchestrator.py`, localiser la fonction :

```python
def _process_memory_action(response_text: str, session_id: str) -> str:
    ...
```

Aujourd’hui, la détection du JSON ressemble à quelque chose comme :

```python
json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
if not json_match:
    return response_text
raw_json = json_match.group(1)
...
```

👉 Problème : si le LLM renvoie juste

```text
```
{ ... }
```
```

ou un bloc sans `json`, on ne matche rien → l’action mémoire n’est jamais exécutée.

### 🔧 Remplacer la détection actuelle par une détection tolérante

Dans `_process_memory_action`, remplacer **tout le bloc de recherche du JSON** par ceci :

```python
    # 1) Essayer d'abord le cas idéal : ```json { ... } ```
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)

    # 2) Si rien trouvé, accepter n'importe quel bloc ``` { ... } ```
    if not json_match:
        json_match = re.search(r"```\s*(\{.*?\})\s*```", response_text, re.DOTALL)

    raw_json = None

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
        return response_text
```

Ensuite, laisser le reste de la fonction faire :
- `json.loads(raw_json)`
- routing vers `save_note`, `save_todo`, `save_process`, etc.

⚠️ Important : ne change PAS la logique métier (mapping `memory_action` → helpers), seulement la partie qui **trouve** le JSON dans `response_text`.

---

## 3. Nettoyer la réponse renvoyée à l’utilisateur

Pour éviter que l’utilisateur voie le bloc JSON brut après exécution de l’action mémoire, on peut nettoyer `response_text` **après** traitement.

Toujours dans `_process_memory_action`, **après** avoir exécuté l’action mémoire (quand tout s’est bien passé), ajouter :

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

    return cleaned or "C'est enregistré."
```

⚠️ Adapter les noms de variables (`fallback_match`, etc.) en fonction de ton implémentation exacte dans `_process_memory_action`.  
L’idée : 
- si on a trouvé un bloc ```…``` → on le supprime de `response_text`,  
- sinon, si on a juste un JSON « nu » → on retire ce JSON,  
- sinon → on renvoie la réponse telle quelle.

---

## 4. Logging (optionnel mais recommandé)

Toujours dans `_process_memory_action`, autour de l’exécution de l’action mémoire, ajouter un petit log, par exemple :

```python
    debug_logger.info({
        "event": "memory_action_executed",
        "session_id": session_id,
        "raw_json": raw_json,
    })
```

ou adapter au système de log déjà utilisé dans ce fichier.

Cela permettra de vérifier facilement dans les logs que :
- le JSON est bien détecté,
- l’action est exécutée,
- on ne dépend plus du strict ```json.

---

## 5. Résumé du patch

1. **Fichier concerné** : `agents/orchestrator.py` uniquement.
2. Rendre `_process_memory_action` **tolérant** aux variantes de format de bloc JSON :
   - ` ```json { ... } ``` `
   - ` ``` { ... } ``` `
   - JSON nu contenant `"memory_action"`.
3. Nettoyer la réponse retournée à l’utilisateur pour **ne plus afficher le JSON brut** quand l’action mémoire est exécutée.
4. (Optionnel) Ajouter un log `memory_action_executed` pour diagnostiquer facilement.

Après le patch, refaire ce test minimal :

1. Lancer Clara
2. Demander : `Sauvegarde une note : demain appeler le plombier`
3. Puis : `Montre-moi toutes mes notes`
4. Vérifier dans les logs que `memory_action_executed` apparaît, et que `NOTES` contient bien 1 entrée.

Si ce test passe, le bug observé sur les notes est corrigé.
