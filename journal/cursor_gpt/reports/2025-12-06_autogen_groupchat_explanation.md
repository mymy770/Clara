# Explication : Fonctionnement des agents Autogen dans le GroupChat

**Date**: 2025-12-06  
**Contexte**: L'utilisateur demande comment fonctionnent les agents du groupe avec Autogen

## Architecture Autogen dans Clara

### 1. Structure du GroupChat

Clara utilise un **GroupChat** avec 3 agents :

```
GroupChat
├── interpreter (AssistantAgent)
│   └── Agent principal qui parle à l'utilisateur
├── fs_agent (AssistantAgent)
│   └── Agent spécialisé filesystem (créer, lire, écrire fichiers/dossiers)
└── memory_agent (AssistantAgent)
    └── Agent spécialisé mémoire (sauvegarder notes, todos, processus, etc.)
```

### 2. Communication entre agents

#### Méthode : Mention (@agent_name)

Les agents communiquent en se **mentionnant** dans leurs messages :

- **Interpreter → fs_agent** : `"@fs_agent, crée le dossier test"`
- **Interpreter → memory_agent** : `"@memory_agent, sauvegarde cette note: ..."`
- **fs_agent → interpreter** : `"✓ Dossier créé : test"` (retour de résultat)
- **memory_agent → interpreter** : `"✓ Note sauvegardée (ID: 123)"` (retour de résultat)

#### Fonctionnement du GroupChatManager

1. **UserProxyAgent** envoie le message utilisateur au **GroupChatManager**
2. Le **GroupChatManager** distribue le message à l'**interpreter** (premier agent)
3. L'**interpreter** analyse la demande :
   - Si opération filesystem → mentionne `@fs_agent`
   - Si opération mémoire → mentionne `@memory_agent`
4. L'agent mentionné répond avec le résultat
5. L'**interpreter** synthétise et répond à l'utilisateur

### 3. Configuration actuelle

```python
groupchat = GroupChat(
    agents=[interpreter, fs_agent, memory_agent],
    messages=[],
    max_round=5,  # Nombre maximum de tours de conversation
    speaker_selection_method="round_robin",  # Chaque agent répond à tour de rôle
)
```

**Paramètres** :
- `max_round=5` : Permet jusqu'à 5 échanges entre agents
- `speaker_selection_method="round_robin"` : Les agents répondent séquentiellement

### 4. Exemple de conversation

**Utilisateur** : "enregistre une note: test autogen"

**Tour 1 - Interpreter** :
```
L'utilisateur demande d'enregistrer une note.
@memory_agent, sauvegarde cette note: test autogen
```

**Tour 2 - MemoryAgent** :
```
✓ Note sauvegardée (ID: 45)
```

**Tour 3 - Interpreter** :
```
Note enregistrée avec succès.
```

### 5. Problèmes identifiés et corrections

#### Problème 1 : Notes non sauvegardées

**Cause** : L'interpreter ne mentionnait pas explicitement `@memory_agent`

**Solution** : Amélioration du `system_message` de l'interpreter pour :
- Expliquer comment mentionner les agents (`@fs_agent`, `@memory_agent`)
- Donner des exemples concrets de délégation
- Insister sur l'exécution immédiate au lieu d'explications

#### Problème 2 : Clara dit "je n'ai pas accès au fichier"

**Cause** : L'interpreter ne savait pas qu'il pouvait demander à `fs_agent` de lire les fichiers

**Solution** : Ajout d'instructions explicites dans le `system_message` :
- "Pour lire un fichier → dis @fs_agent, lis le fichier X"
- "Ne dis PAS 'je ne peux pas accéder au système de fichiers'. Tu as fs_agent pour ça."

#### Problème 3 : max_round trop faible

**Cause** : `max_round=3` ne permettait pas assez de tours pour la délégation

**Solution** : Augmentation à `max_round=5` pour permettre :
1. Interpreter reçoit la demande
2. Interpreter mentionne l'agent spécialisé
3. Agent spécialisé exécute et répond
4. Interpreter synthétise
5. (Tour supplémentaire si nécessaire)

### 6. Tools (fonctions) des agents

#### fs_agent
- `create_dir(path)` : Créer un dossier
- `create_file(path, content)` : Créer un fichier
- `read_file(path)` : Lire un fichier
- `append_to_file(path, content)` : Ajouter du contenu
- `list_dir(path)` : Lister un dossier
- `move_path(src, dst)` : Déplacer/renommer
- `delete_path(path)` : Supprimer

#### memory_agent
- `save_note_tool(content, tags)` : Sauvegarder une note
- `list_notes()` : Lister toutes les notes
- `save_todo_tool(content, tags)` : Sauvegarder un todo
- `list_todos()` : Lister tous les todos
- `save_process_tool(content, tags)` : Sauvegarder un processus
- `list_processes()` : Lister tous les processus
- `save_protocol_tool(content, tags)` : Sauvegarder un protocole
- `list_protocols()` : Lister tous les protocoles
- `save_preference_tool(key, value, scope)` : Sauvegarder une préférence
- `list_preferences_tool()` : Lister toutes les préférences
- `search_memory(query)` : Rechercher dans la mémoire

### 7. Flux complet (exemple : sauvegarder une note)

```
1. UserProxyAgent → GroupChatManager
   Message: "enregistre une note: test"

2. GroupChatManager → Interpreter
   Message: "enregistre une note: test"

3. Interpreter analyse et décide :
   → C'est une opération mémoire
   → Il doit mentionner @memory_agent

4. Interpreter → GroupChatManager
   Message: "@memory_agent, sauvegarde cette note: test"

5. GroupChatManager → MemoryAgent
   Message: "@memory_agent, sauvegarde cette note: test"

6. MemoryAgent exécute :
   → Appelle save_note_tool("test", None)
   → Fonction Python sauvegarde dans SQLite
   → Retourne "✓ Note sauvegardée (ID: 45)"

7. MemoryAgent → GroupChatManager
   Message: "✓ Note sauvegardée (ID: 45)"

8. GroupChatManager → Interpreter
   Message: "✓ Note sauvegardée (ID: 45)"

9. Interpreter synthétise :
   → Note que la note a été sauvegardée
   → Formule une réponse utilisateur-friendly

10. Interpreter → GroupChatManager
    Message: "Note enregistrée avec succès."

11. GroupChatManager → UserProxyAgent
    Réponse finale: "Note enregistrée avec succès."
```

### 8. Avantages de cette architecture

1. **Séparation des responsabilités** : Chaque agent a un rôle précis
2. **Réutilisabilité** : Les agents peuvent être utilisés indépendamment
3. **Extensibilité** : Facile d'ajouter de nouveaux agents (ex: `calendar_agent`, `email_agent`)
4. **Debugging** : Chaque interaction est visible dans les logs
5. **Flexibilité** : L'interpreter peut orchestrer plusieurs agents pour une tâche complexe

### 9. Limitations actuelles

1. **Pas de fonction calling automatique** : Les agents doivent être mentionnés explicitement
2. **Dépendance au LLM** : L'interpreter doit "comprendre" quand déléguer
3. **Pas de validation croisée** : Les agents ne vérifient pas mutuellement leurs actions

### 10. Améliorations futures possibles

1. **Function calling automatique** : L'interpreter pourrait appeler directement les fonctions des agents
2. **Validation croisée** : Un agent pourrait vérifier le travail d'un autre
3. **Planification multi-agents** : L'interpreter pourrait créer un plan et le distribuer aux agents
4. **Cache partagé** : Les agents pourraient partager un cache pour éviter les appels redondants

