# Schéma Contact – Phase 2
Date: 2025-12-05

## Contexte

Clara a maintenant besoin de gérer des contacts de manière structurée. Les contacts sont plus complexes que les simples notes/todos car ils ont plusieurs champs (nom, téléphones, emails, relations, etc.).

## Schéma final retenu

### Structure JSON dans la table `memory`

Pour `type = 'contact'`, le champ `content` contient un JSON avec :

```json
{
  "first_name": "Aurélie",
  "last_name": "Malai",
  "display_name": "Aurélie Malai",
  
  "aliases": ["ma femme", "mon épouse"],
  
  "category": "family",
  "relationship": "wife",
  
  "phones": [
    {
      "number": "+972-5x-xxx-xxxx",
      "label": "mobile perso",
      "primary": true,
      "channels": ["call", "sms", "whatsapp"]
    }
  ],
  
  "emails": [
    {
      "address": "aurelie@example.com",
      "label": "perso",
      "primary": true
    }
  ],
  
  "company": "Active Games",
  "role": "Associée / co-fondatrice",
  
  "notes": [
    "Prépare les deals fournisseurs LED"
  ]
}
```

## Décisions importantes

### 1. Champ `importance` → SUPPRIMÉ

**Raison :** Tous les contacts sont importants. Pas besoin de hiérarchie pour l'instant.

### 2. Champ `emails[].tags` → SUPPRIMÉ  

**Raison :** Simplification. On garde juste `label` + `primary`.

### 3. `aliases` → Liste

**Format :** `["ma femme", "mon frère", "Paulo", ...]`

**Utilité :** Permet de retrouver un contact par son surnom ou sa relation.

### 4. `phones[].channels` → Liste

**Format :** `["call", "sms", "whatsapp", "telegram"]`

**Utilité :** Savoir quels modes de communication sont disponibles pour ce numéro.

### 5. Plusieurs téléphones/emails possibles

Un contact peut avoir :
- Plusieurs numéros (perso, pro, autres)
- Plusieurs emails (perso, pro, autres)
- Un `primary` par type (le code ne valide pas encore, mais c'est prévu)

## Prochaines étapes

- Intégration dans l'orchestrator (intentions JSON)
- UI pour visualiser/éditer les contacts
- Validation (pas de doublons, format téléphone, etc.)
- Relations entre contacts




