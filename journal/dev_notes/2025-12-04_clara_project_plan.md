# Clara – Plan global (version initiale)
Date: 2025-12-04

## 1. Objectif général

Construire une nouvelle Clara, propre et stable, basée sur :
- Un orchestrateur central (Clara) avec agents spécialisés (FS, Mail, Calendar, WhatsApp, etc.).
- Une mémoire sérieuse (base structurée + éventuellement vecteurs) avant les outils complexes.
- Une architecture testable, versionnée (GitHub) et observable (logs / journal de dev).

On repart de zéro sur l’infra, mais on pourra réutiliser des idées/drivers là où c’est pertinent.

---

## 2. Structure du repo GitHub (proposition)

```text
clara/
  agents/
    orchestrator.py        # Clara, cerveau central
    fs_agent.py            # Agent filesystem (phase 1)
    mail_agent.py          # Agent mail (phase ultérieure)
    calendar_agent.py      # Agent agenda
    whatsapp_agent.py      # Agent WhatsApp
  drivers/
    fs_driver.py           # Accès fichiers/dossiers
    gmail_driver.py
    calendar_driver.py
    whatsapp_driver.py
  memory/
    schema.sql             # Schéma SQLite
    migrations/            # Évolution du schéma
    memory_core.py         # API mémoire (lecture/écriture)
    vector/                # Optionnel : index vectoriel (plus tard)
      readme.md
  config/
    agents.yaml            # Définition des agents, rôles, modèles, paramètres
    settings.yaml          # Réglages globaux (paths, langue, etc.)
    env.example            # Exemple de variables d’environnement
  logs/
    sessions/
      session_2025-12-04_12-00.session.json  # conversation humaine
      session_2025-12-04_12-00.debug.json    # log technique complet
  ui/
    chat_frontend/         # UI de chat (existante, reconnectée)
    admin_frontend/        # UI admin/monitoring (plus tard)
  journal/
    dev_notes/
      2025-12-04_initial_project_plan.md
      2025-12-05_phase1_decisions.md
  tests/
    test_fs_agent.py
    test_memory_core.py
    test_mail_agent.py
  run_clara.py             # Entrée principale pour lancer Clara localement
  README.md
```

---

## 3. Politique de logs

### 3.1 Deux fichiers par session

Pour chaque session (un “run” utilisateur complet) :

- **1 fichier session (humain)**  
  `logs/sessions/<session_id>.session.json`  
  Contient uniquement :
  - messages utilisateur
  - réponses de Clara (texte final)
  - métadonnées légères (date, durée, id)

Objectif : relire une conversation comme un chat.

- **1 fichier debug (technique complet)**  
  `logs/sessions/<session_id>.debug.json`  
  Contient TOUT ce qui est utile pour le debug :
  - prompts envoyés au LLM (THINK/PLAN/EXEC/RESPOND ou équivalent AutoGen)
  - appels aux tools/agents
  - paramètres des calls
  - réponses brutes des drivers
  - erreurs, stack traces
  - temps de chaque étape
  - décisions de l’orchestrateur

Objectif : permettre à toi / Cursor / n’importe quel dev de reconstruire ce qui s’est passé, sans rien perdre.

### 3.2 Format

- JSON structuré (pas JSONL) pour faciliter l’analyse.
- Clé obligatoire dans le debug :
  - `session_id`
  - `timestamp`
  - `actor` (user, clara, agent_x, driver_y)
  - `type` (message, tool_call, tool_result, error)
  - `payload` (données libres)

---

## 4. Journal de développement

Tout ce qu’on décide / teste / corrige doit être tracé.

- **Dossier** : `journal/dev_notes/`
- **Format** : un fichier markdown par jour ou par étape clé.
  - `YYYY-MM-DD_description.md`
- Contenu recommandé :
  - contexte de la journée
  - décisions prises
  - problèmes rencontrés
  - solutions testées (même celles rejetées)
  - liens vers commits/prs importants
  - idées pour la suite

Exemples :
- `2025-12-04_initial_project_plan.md`
- `2025-12-06_phase1_fs_agent_stable.md`
- `2025-12-10_memory_schema_v1.md`

Le but : garder l’historique de l’évolution, bon ET mauvais.

---

## 5. Mémoire : architecture (non “simple” au sens faible)

### 5.1 Base principale : SQLite solide

SQLite ici = **moteur de base de données embarqué**, pas une “mémoire simple” au sens “basique”.  
L’idée est d’avoir une **base structurée, durable, migrable**.

Schéma de base (à faire évoluer) :
- `users` (si multi-personnes)
- `contacts` (nom, téléphone, email, relations, tags…)
- `preferences` (clé, valeur, portée : globale / par agent / par contexte)
- `protocols` (procédures / checklists / workflows définis)
- `memory_events` (événements marquants, logs structurés par Clara)
- `agent_state` (état persistant par agent si nécessaire)

Tu pourras ensuite :
- faire des migrations propres (ajout de colonnes, tables),
- requêter précisément (ex : tous les contacts liés à “ma femme”),
- garder une base unique et robuste.

### 5.2 Mémoire vectorielle (phase 2b ou 3)

Pour tout ce qui est texte libre (grandes discussions, docs, historiques), on pourra ajouter :

- un **index vectoriel** (soit via extension SQLite type sqlite-vss, soit via un service séparé type Qdrant/Weaviate).
- stocker :
  - embeddings de conversations
  - extraits de mails
  - notes longues, etc.

Clara pourra combiner :
- **mémoire structurée (SQL)** pour les choses précises et importantes (contacts, protocoles, prefs).  
- **mémoire vectorielle** pour retrouver du contexte flou (“quand est-ce qu’on a parlé de X ?”).

### 5.3 Types de mémoire (concept)

On pourra progressivement organiser la mémoire en :
- **court terme** (contexte session en cours)
- **moyen terme** (dernières sessions marquantes)
- **long terme** (faits stabilisés : relations, préférences, décisions importantes)
- **par agent** mais centralisée (les agents écrivent dans la même base, avec un champ `agent_id`).

Mais ça se construit en plusieurs itérations, sur la même base SQLite + (plus tard) vecteur.

---

## 6. UI de chat vs UI admin

### 6.1 UI de chat

- On **garde l'UI de chat existante** comme interface principale pour parler à Clara.
- Dès la **Phase 1**, l'UI de chat est reconnectée à la nouvelle Clara (orchestrateur + FS-Agent).
- Objectif : pouvoir parler à Clara très tôt, même si elle n'a que des capacités FS + reporting de base.

### 6.2 UI admin / backend

- UI séparée ou onglet dans la même app (ex : `/admin` ou “Paramètres Clara”).
- Fonctions prévues :
  - voir la liste des agents (nom, rôle, état)
  - voir la liste des drivers/tools installés
  - consulter les sessions récentes (avec lien vers logs)
  - voir les erreurs récurrentes
  - éventuellement, éditer des paramètres (température, modèles, timeouts).

Ordre de priorité réaliste :
1. Phase 1 : UI de chat reconnectée.
2. Phase 2 : Mémoire + FS fonctionnels.
3. Phase 3 : UI admin minimale (liste agents + accès aux logs).
4. Phases suivantes : UI admin plus avancée (gestion des workflows, stats).

---

## 7. Roadmap globale (haute altitude)

### Phase 1 – Fondation Clara
- Orchestrateur Clara (AutoGen ou autre framework multi-agents).
- FS-Agent robuste : lire/écrire/lister fichiers, petits rapports.
- Logging structuré (2 fichiers par session).
- Repo GitHub structuré + démarrage du journal de dev.
- UI de chat existante reconnectée à cette nouvelle base.

### Phase 2 – Mémoire solide
- Mise en place de la base SQLite (schema v1).
- API mémoire (lecture / écriture / mise à jour / suppression).
- Intégration avec Clara : préférences, contacts de base, protocols.
- Début de séparation court/moyen/long terme au niveau conceptuel.
- Journalisation des décisions autour du schéma mémoire.

### Phase 3 – UI admin minimale
- Page / onglet admin :
  - visualisation des agents et de leur état
  - liste des sessions récentes
  - accès simplifié aux logs (session + debug)
- Ajustements mémoire/FS selon retour d’usage.

### Phase 4 – Agents outils (un par un)
- MailAgent + driver (ou MCP) pour Gmail.
- CalendarAgent + driver (ou MCP) pour agenda.
- WhatsAppAgent + driver (ou MCP) pour WhatsApp.
- Pour chaque agent :
  - scénarios de test réels (comme tu fais déjà)
  - logs et corrections jusqu’à stabilisation
  - notes dans journal/

### Phase 5 – Automatisation avancée
- Protocoles et workflows plus complexes (multi-agents).
- TODO list interne par mission (avec suivi dans les logs).
- Mise en place d’une couche “règles” (ce que Clara peut/peut pas faire).
- Optimisation mémoire (ajout index vectoriel si besoin).

---

## 8. Prochaines étapes

1. **Valider ou ajuster ce plan global** (ce document).  
2. Créer le repo GitHub `Clara`.  
3. Y pousser une version minimale avec :
   - structure de dossiers
   - squelette `run_clara.py`
   - README.md avec ce plan résumé
   - premier fichier de journal dans `journal/dev_notes/`.
4. Ensuite, détailler la **Phase 1** (design précis de Clara + FS-Agent + format logs).

Ce document sert de référentiel haut niveau.  
Les détails de la Phase 1 seront dans un fichier séparé (ex: `journal/dev_notes/2025-12-04_phase1_design.md`).