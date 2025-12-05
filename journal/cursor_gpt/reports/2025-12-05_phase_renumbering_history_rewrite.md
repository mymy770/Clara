# Renumérotation des Phases + Réécriture Historique Git
Date: 2025-12-05

## Contexte

Le projet Clara avait une incohérence de numérotation : la mémoire était appelée "Phase 3" dans le code et les commits, alors que le plan officiel la définit comme "Phase 2 – Mémoire solide".

**Plan officiel :**
- Phase 0 : Infrastructure
- Phase 1 : Fondation Clara
- **Phase 2 : Mémoire solide** ← (était appelée Phase 3 par erreur)
- Phase 3 : UI Admin
- Phase 4 : Agents outils
- Phase 5 : Automatisation avancée

**Objectif :** Harmoniser TOUT le projet avec ce plan.

## Liste des commits modifiés

### Commits réécrits (messages modifiés)

**Avant → Après :**

1. `Phase 3: connect orchestrator to memory core (notes basics)`
   → `Phase 2: connect orchestrator to memory core (notes basics)`

2. `Phase 3.5: extend memory to todo/process/protocol`
   → `Phase 2.5: extend memory to todo/process/protocol`

3. `Archive retroactive: phase3 fix orchestrator autotags mission`
   → `Archive retroactive: phase2 fix orchestrator autotags mission`

**Total :** 3 messages de commits modifiés

### Autres commits (non modifiés)

Les commits ne concernant pas la mémoire ont été préservés tels quels :
- Commits Phase 1
- Commits Phase 2 originaux (memory core)
- Commits de fixes et corrections
- Commits d'infrastructure

## Commandes principales utilisées

### 1. Scan des commits à modifier

```bash
git log --oneline | grep -i "phase 3\|phase3"
```

**Résultat :** 3 commits identifiés

### 2. Réécriture des messages

```bash
git filter-branch -f --msg-filter 'sed "s/Phase 3\.5/Phase 2.5/g; s/Phase 3:/Phase 2:/g; s/phase3/phase2/g"' -- --all
```

**Effet :**
- Parcourt TOUS les commits
- Applique les remplacements dans les messages
- Crée un nouvel historique propre

### 3. Push force sur origin

```bash
git push --force origin main
```

**Effet :**
- Remplace l'historique distant par le nouvel historique local
- ⚠️ Opération irréversible

## Résultat final

### Historique Git propre

```bash
git log --oneline | head -10
```

**Nouveaux messages :**
- ✅ "Phase 2: add contacts schema and renumber phases (3→2 for memory)"
- ✅ "Phase 2.5: extend memory to todo/process/protocol"
- ✅ "Phase 2: connect orchestrator to memory core (notes basics)"
- ✅ "Archive retroactive: phase2 fix orchestrator autotags mission"

Aucune mention de "Phase 3" pour la mémoire.

### Fichiers renommés

**Instructions :**
- phase3_memory_integration → phase2_memory_integration
- phase3_5_memory_todo → phase2_5_memory_todo
- phase3_fix_orchestrator → phase2_fix_orchestrator

**Reports :** (même renommage)

**Extensions :**
- .txt → .md pour tous les fichiers instructions/reports

### Code mis à jour

**`agents/orchestrator.py` :**
- "Phase 3.5" → "Phase 2.5"

**README.md :**
- Roadmap déjà correcte (aucun changement nécessaire)

## Vérifications post-rewrite

✅ Historique Git cohérent avec le plan officiel
✅ Aucun commit orphelin
✅ Branche main mise à jour sur origin
✅ Fichiers locaux synchronisés
✅ Aucune perte de données

## Avertissements

**⚠️ Force Push utilisé**

Le push force a remplacé l'historique distant. Si quelqu'un d'autre avait cloné le repo, il devra :
```bash
git fetch origin
git reset --hard origin/main
```

**Contexte :** Jeremy est le seul développeur sur ce repo, donc pas de conflit.

## Conclusion

**Renumérotation complète ✅ TERMINÉE**

Le projet Clara est maintenant 100% cohérent :
- ✅ Historique Git harmonisé
- ✅ Fichiers renommés
- ✅ Code mis à jour
- ✅ Documentation alignée
- ✅ Plan officiel respecté

**Phase 2 = Mémoire solide** partout dans le projet ! 🎯📝




