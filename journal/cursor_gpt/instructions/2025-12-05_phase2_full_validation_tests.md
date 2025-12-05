# 2025-12-05 — Plan de tests complets mémoire + contacts

## 🎯 Objectif

Vérifier **de bout en bout** que tout ce qui existe aujourd’hui fonctionne vraiment, sans bug caché :

- Mémoire structurée : `note`, `todo`, `process`, `protocol`, `preference`
- Contacts : création, lecture, mise à jour, recherche
- Intégration avec l’orchestrateur : intents JSON → actions mémoire réelles
- Cohérence entre `schema.sql`, `memory_core.py`, `helpers.py`, `contacts.py`, `orchestrator.py`

Tu es en **mode agent** et tu dois :

1. Mettre à jour / créer les tests nécessaires.
2. Exécuter les tests.
3. Produire un **rapport clair** dans le journal de dev.
4. Ne PAS modifier la logique métier si ce n’est pas strictement nécessaire pour corriger un bug avéré.

---

## 1. Fichiers à analyser avant tout

Lis et comprends les fichiers suivants (lecture seule, pas de refactor au pif) :

- `agents/orchestrator.py`
- `memory/memory_core.py`
- `memory/helpers.py`
- `memory/schema.sql`
- `memory/contacts.py`
- `config/settings.yaml`
- `config/agents.yaml`
- `journal/dev_notes/2025-12-04_clara_project_plan.md`
- Tous les derniers journaux liés à la mémoire / contacts :
  - `journal/cursor_gpt/2025-12-05_phase2_memory_*.md`
  - `journal/cursor_gpt/2025-12-05_phase2_contacts_*.md`
  - `journal/cursor_gpt/2025-12-05_debug_save_note_fix.md` (si présent)

But : **ne rien supposer**, tout vérifier par le code actuel.

Crée ensuite un nouveau journal :  
`journal/cursor_gpt/2025-12-05_phase2_full_validation.md` avec :

- Contexte des tests
- Liste des fichiers analysés
- Hypothèses initiales

---

## 2. Préparation de la base mémoire (sandbox de test)

But : avoir une base propre pour ne pas mélanger les vieux tests avec les nouveaux.

1. Sauvegarder le fichier actuel si présent :
   - Si `memory/memory.sqlite` existe → le renommer en :
     - `memory/memory_backup_2025-12-05_before_full_validation.sqlite`

2. Recréer une base propre :
   - Vérifier que `memory/schema.sql` est aligné avec le code.
   - Créer un nouveau `memory/memory.sqlite` basé sur `schema.sql`.
   - Vérifier que les tables suivantes existent :
     - `memory`
     - `contacts`
     - `preferences` (si déjà implémentée, sinon noter dans le rapport)

3. Documenter dans le journal :
   - Chemin de la base utilisée
   - Taille initiale (nombre de lignes dans chaque table)

⚠️ Ne touche pas à la logique métier ici. On prépare juste un terrain propre.

---

## 3. Batterie de tests manuels via `run_clara.py`

Objectif : vérifier que **depuis le chat**, tout fonctionne vraiment comme prévu.

### 3.1. Script de test à exécuter dans le terminal

Prépare dans le journal un bloc “Script de test manuel” que Jeremy pourra suivre, par exemple :

```text
1. Lance Clara :  
   python3 run_clara.py

2. Dans le chat, poser EXACTEMENT ces questions dans cet ordre :

   a) "Sauvegarde une note : demain appeler le plombier"
   b) "Sauvegarde un todo : préparer le dossier pour le banquier"
   c) "Sauvegarde un process : comment je prépare une réunion importante"
   d) "Sauvegarde un protocole : ma façon idéale de gérer les mails"
   e) "Ajoute une préférence : je préfère les résumés courts pour les mails"
   f) "Ajoute un contact : Aurélie, ma femme, numéro +33..., email ..., relation : femme"
   g) "Montre-moi toutes mes notes"
   h) "Montre-moi tous mes todos"
   i) "Montre-moi tous mes process"
   j) "Montre-moi tous mes protocoles"
   k) "Montre-moi toutes mes préférences"
   l) "Montre-moi la fiche contact d'Aurélie"
```

Tu dois :

- Définir clairement ce que Clara **doit répondre** à chaque étape.
- Spécifier ce qui doit être **enregistré en base** à chaque action.

### 3.2. Vérifications automatiques associées

Après l’exécution manuelle du script par Jeremy, tu devras :

- Lancer un petit script de vérification (voir section 4) qui :
  - Compte le nombre de `note`, `todo`, `process`, `protocol`, `preference`.
  - Vérifie que les contenus correspondent bien aux phrases envoyées.
  - Vérifie que le contact “Aurélie” a bien les bons champs (nom, relation, numéros, emails, tags).

---

## 4. Tests automatisés — `tests/test_memory_contacts_end_to_end.py`

Crée un nouveau fichier de tests :

- `tests/test_memory_contacts_end_to_end.py`

Avec au minimum :

### 4.1. Tests direct de `memory_core` + `helpers`

Tests unitaires/integ :

- `test_save_and_load_note()`
  - utilise directement `save_item` ou `save_note`
  - vérifie que :
    - la ligne existe en base
    - `type = 'note'`
    - `content` match
    - `tags` correctement serialisés/déserialisés

- `test_save_todo_process_protocol()`
  - même principe pour `todo`, `process`, `protocol`

- `test_save_preference()`
  - si `preferences` est en table séparée → utiliser la bonne API
  - sinon → type = 'preference' dans `memory`

- `test_contacts_crud()`
  - création d’un contact minimal
  - ajout de numéros avec labels / channels
  - mise à jour d’un champ
  - lecture par `id` ou par `name`
  - recherche par tag / relation (si implémenté)

Ces tests doivent être **idempotents** et pouvoir tourner sur la base de test préparée en section 2.

### 4.2. Tests sur l’orchestrateur (facultatif mais idéal)

Optionnel si c’est simple à faire :

- Simuler un `LLM` qui renvoie un bloc JSON d’intentions (memory_action)
- Vérifier que `_process_memory_action` déclenche bien les bons helpers sans erreur.

---

## 5. Rapport final dans le journal

À la fin, tu dois compléter :

`journal/cursor_gpt/2025-12-05_phase2_full_validation.md` avec les sections :

1. **Contexte**
   - Ce qu’on a voulu valider

2. **Fichiers analysés**
   - Liste + remarques (cohérence schema/code, éventuels warnings)

3. **Base de données**
   - Chemin utilisé
   - Tables présentes
   - État initial / final (nombre de lignes par type)

4. **Tests manuels**
   - Script exact exécuté par Jeremy
   - Résultats observés (OK / KO) pour chaque étape
   - Screens / extraits de réponses si utile

5. **Tests automatisés**
   - Liste des tests créés dans `tests/`
   - Résultat : OK / KO
   - Détails des éventuelles erreurs

6. **Bugs trouvés**
   - Description courte de chaque bug
   - Fichier(s) impliqué(s)
   - Gravité (bloquant / gênant / cosmétique)
   - Si corrigé : oui/non (et dans quel commit)

7. **Conclusion**
   - Est-ce qu’on peut considérer la phase “Mémoire + Contacts” comme :
     - ✅ Stable pour continuer vers la suite
     - ⚠️ Utilisable mais encore fragile
     - ❌ Pas prête (expliquer pourquoi)

⚠️ Important :  
Ce patch est **uniquement un plan de tests + modifications de tests**.  
Tu **ne touches pas à la logique métier** (orchestrator, helpers, contacts) sauf si :

- un test révèle un bug réel,
- tu documentes ce bug dans le journal,
- tu appliques un fix **minimal**, clairement décrit dans le rapport.
