# 2025-12-06 – Patch UI : Panneau Détails internes

## Contexte

Mission : Reconnecter l'UI aux infos internes de Clara (réflexion, plan d'action, étapes exécutées) **sans toucher au backend**, en utilisant ce qui est déjà renvoyé par l'API.

**Objectif** : Créer un panneau "Détails internes" repliable avec 3 sections (Réflexion, Plan d'action, Étapes exécutées) pour afficher les données internes de Clara.

---

## Changements implémentés

### 1. Modification de l'orchestrator pour renvoyer les données internes

**Fichier modifié** : `agents/orchestrator.py`

**Changements** :
- `handle_message()` retourne maintenant un `dict` avec `{'response': str, 'internal': dict}` au lieu d'une simple string
- Nouvelle méthode `_extract_internal_data()` qui extrait :
  - **Réflexion** : depuis `memory_context` (données pré-chargées) ou premières lignes de la réponse
  - **Plan d'action** : depuis `memory_result` si c'est un plan/todo
  - **Étapes exécutées** : depuis `memory_result` si des actions mémoire ont été exécutées

**Format retourné** :
```python
{
    'response': 'Réponse textuelle de Clara',
    'internal': {
        'thoughts': str ou None,
        'todo': str ou None,
        'steps': list ou None
    }
}
```

**Compatibilité** : Gestion du cas d'erreur pour retourner aussi un dict.

### 2. Adaptation de l'API backend

**Fichier modifié** : `api_server.py`

**Changements** :
- `ChatResponse` : Ajout du champ `internal: Optional[dict] = None`
- `/chat` endpoint : Extraction des données internes depuis la réponse de l'orchestrator
- Les données internes sont toujours renvoyées (pas seulement si `debug=True`)

**Format réponse API** :
```json
{
    "reply": "Réponse de Clara",
    "session_id": "session_...",
    "internal": {
        "thoughts": "...",
        "todo": "...",
        "steps": [...]
    }
}
```

### 3. Adaptation de run_clara.py

**Fichier modifié** : `run_clara.py`

**Changements** :
- Gestion du nouveau format de retour (dict au lieu de string)
- Extraction de `response` depuis le dict pour l'affichage et le logging
- Compatibilité avec l'ancien format (string) pour éviter les erreurs

### 4. Nouveau composant InternalPanel

**Nouveau fichier** : `ui/chat_frontend/src/components/InternalPanel.jsx`

**Fonctionnalités** :
- Panneau repliable à droite (visible si RightPanel est fermé)
- 3 sections :
  1. **🧠 Réflexion** : Affiche les pensées internes (max 4 lignes)
  2. **✅ Plan d'action** : Affiche le plan/todo (max 10 lignes)
  3. **⚙️ Étapes exécutées** : Affiche les actions mémoire exécutées (max 10 items)
- Gestion défensive : Si une donnée est `null`, affiche "Aucune ... disponible"
- Support de différents formats : string, array, object (avec JSON.stringify si nécessaire)

**Style** :
- Utilise les variables CSS du thème (`--right-panel-bg`, `--text-color`, etc.)
- Largeur : 280px
- Scroll vertical si contenu long
- Style sobre et lisible

### 5. Intégration dans App.jsx

**Fichier modifié** : `ui/chat_frontend/src/App.jsx`

**Changements** :
- Ajout de l'état React :
  - `internalPanelOpen` : contrôle l'affichage du panneau
  - `internalThoughts`, `internalTodo`, `internalSteps` : stockent les données internes
- Extraction des données depuis `response.internal` dans `handleSendMessage()`
- Bouton "Détails" dans le header (visible uniquement si RightPanel est fermé)
- Intégration du composant `InternalPanel` dans le layout

**Logique d'affichage** :
- RightPanel ouvert → InternalPanel caché
- RightPanel fermé → Bouton "Détails" visible → InternalPanel peut s'ouvrir

---

## Fichiers créés

1. `ui/chat_frontend/src/components/InternalPanel.jsx` – Panneau détails internes
2. `journal/cursor_gpt/instructions/2025-12-06_ui_internal_panel_patch.md` – Instructions (déplacé)
3. `journal/cursor_gpt/reports/2025-12-06_ui_internal_panel_patch.md` – Ce rapport

## Fichiers modifiés

1. `agents/orchestrator.py` – Retourne dict avec `response` + `internal`, méthode `_extract_internal_data()`
2. `api_server.py` – Gestion du nouveau format, ajout champ `internal` à `ChatResponse`
3. `run_clara.py` – Adaptation pour gérer le nouveau format de retour
4. `ui/chat_frontend/src/App.jsx` – Intégration InternalPanel avec état React et extraction données

---

## Limitations connues

1. **Données internes minimales** : Pour l'instant, les données extraites sont basiques :
   - Réflexion : Premières lignes de la réponse ou contexte mémoire
   - Plan : Détecté depuis `memory_result` si contient "todo" ou "plan"
   - Étapes : Détectées depuis `memory_result` si contient "sauvegardé", "enregistré", etc.

2. **Pas de données depuis le prompt** : Les données internes ne sont pas encore extraites depuis le prompt système ou les messages intermédiaires du LLM.

3. **Pas de données depuis DebugLogger** : Les données du `DebugLogger` (prompt_messages, llm_response brute) ne sont pas encore exposées dans l'API.

4. **Affichage conditionnel** : Le panneau InternalPanel n'est visible que si RightPanel est fermé (pour éviter la surcharge).

---

## Tests à réaliser

✅ **Backend** :
- Vérifier que l'orchestrator retourne bien un dict avec `response` et `internal`
- Vérifier que l'API renvoie bien `internal` dans la réponse JSON
- Vérifier que `run_clara.py` fonctionne toujours en mode terminal

✅ **Frontend** :
- Envoyer un message à Clara
- Vérifier dans la console que `response.internal` contient des données
- Ouvrir le panneau "Détails internes" (bouton "Détails" dans le header)
- Vérifier que les 3 sections s'affichent correctement
- Vérifier que le panneau est repliable

✅ **Données** :
- Tester avec une action mémoire (ex: "sauvegarde une note")
- Vérifier que "Étapes exécutées" affiche l'action
- Tester avec une demande de liste (ex: "liste mes notes")
- Vérifier que "Réflexion" affiche le contexte mémoire pré-chargé

---

## Conclusion

Le panneau "Détails internes" est maintenant fonctionnel avec :
- Extraction des données internes depuis l'orchestrator
- Exposition via l'API sans modification majeure du backend
- Affichage dans un panneau repliable à droite
- 3 sections (Réflexion, Plan, Étapes) avec gestion défensive

Les données sont encore basiques, mais la structure est en place pour être enrichie progressivement avec plus de données depuis le prompt, le DebugLogger, ou d'autres sources.

