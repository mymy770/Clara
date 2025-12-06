# Explication Simple : Comment Autogen Fonctionne VRAIMENT

**Date**: 2025-12-06  
**Contexte**: L'utilisateur ne comprend pas pourquoi Autogen ne gère pas automatiquement la communication entre agents

## Le Problème Actuel

Tu as raison : **Autogen EST censé gérer automatiquement la communication et l'appel des fonctions**. Mais actuellement, ça ne marche pas.

## Comment Autogen Fonctionne VRAIMENT

### 1. Function Calling Automatique

Autogen utilise le **function calling d'OpenAI** :
- Les fonctions dans `function_map` sont converties en "tools" OpenAI
- Le LLM voit ces tools dans sa liste de fonctions disponibles
- Le LLM décide automatiquement d'appeler une fonction quand c'est pertinent
- Autogen exécute la fonction et retourne le résultat au LLM

### 2. Communication Inter-Agents

Dans un GroupChat :
- Les agents peuvent se mentionner (`@memory_agent`)
- MAIS le vrai mécanisme est le **function calling** : chaque agent a ses propres fonctions
- Quand l'interpreter veut sauvegarder une note, il devrait appeler directement `save_note_tool` (pas besoin de mentionner @memory_agent)

### 3. Le Problème Actuel

**Ce qui ne marche pas** :
- Les fonctions sont dans `function_map` ✓
- Les fonctions sont enregistrées avec `register_for_llm` ✓
- MAIS le LLM ne les appelle pas automatiquement ✗

**Pourquoi ?**
- Le LLM ne voit peut-être pas les fonctions comme des "tools" disponibles
- Il faut vérifier que les fonctions sont bien converties en format OpenAI tools

## Solution : Vérifier la Conversion en Tools

Autogen doit convertir les fonctions en format OpenAI tools. Vérifions que ça fonctionne.

