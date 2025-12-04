# Cursor Instructions – Journaling & Project Discipline Setup

## 1. Journaux de conception (journal/dev_notes)

Cursor doit créer et maintenir des journaux de conception dans :
    journal/dev_notes/

Chaque fichier doit suivre le format :
    YYYY-MM-DD_titre.md

Objectif :
- documenter les décisions techniques  
- documenter l’architecture  
- enregistrer les évolutions structurelles du projet  

Un journal est créé UNIQUEMENT lorsqu’il y a :
- une décision d’architecture  
- une évolution d’infrastructure  
- une définition de module (FS, Memory, Agents…)  
- une refonte importante  
- une résolution de problème structurante  

### Format standard :
```
# Titre
Date: YYYY-MM-DD

## Contexte
(3–4 lignes maximum)

## Décisions
- ...

## Changements apportés
- ...

## Prochaines étapes
- ...
```

⚠️ Aucun code ne doit apparaître dans ces fichiers.


## 2. Différence avec les journaux runtime (logs)

Les journaux runtime dans `logs/sessions/` seront générés plus tard par Clara elle-même.  
Cursor **ne doit jamais écrire dedans**.


## 3. Création du fichier `journal/README.md`

Cursor doit créer :
```
journal/README.md
```

Contenu :
```
# Journal de conception Clara

Ce dossier contient l’historique des décisions d’architecture du projet Clara.

Règles :
1. Un fichier par grande décision ou évolution.
2. Respecter le format standard (Contexte, Décisions, Changements, Prochaines étapes).
3. Aucun code ne doit apparaître dans ces fichiers.
4. Ces journaux servent uniquement à suivre l’évolution technique et conceptuelle du projet.
```


## 4. Gestion des instructions dans `gpt_cursor/`

Toutes les requêtes utilisateur destinées à Cursor seront placées dans :
```
gpt_cursor/
```

Pour chaque fichier d’instruction :

1. Cursor lit et exécute les instructions.
2. Cursor crée un fichier d’archive dans :
```
journal/cursor_gpt/YYYY-MM-DD_nom_requete.md
```
3. Ce fichier doit contenir :
   - Contexte  
   - Instructions reçues  
   - Actions effectuées  
   - Changements réalisés  
   - Prochaines étapes (si nécessaire)  

4. Cursor déplace ensuite le fichier original depuis `gpt_cursor/` vers :
```
journal/cursor_gpt/
```

→ Ainsi, **chaque intervention de Cursor est historisée proprement**.


## 5. Rappel fondamental : aucune implémentation à cette phase

Cursor ne doit PAS :
- implémenter des agents  
- écrire du code fonctionnel  
- générer de la logique métier  

Il doit UNIQUEMENT :
- mettre en place l’infrastructure  
- écrire les journaux  
- maintenir l’hygiène et la discipline du projet Clara  
