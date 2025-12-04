# Clara - Assistant IA Intelligent

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Status](https://img.shields.io/badge/status-en%20développement-orange)

## 📋 Vue d'ensemble

Clara est une refonte complète de l'assistant IA Clara, construite sur une architecture propre et modulaire avec :
- Un orchestrateur central coordonnant des agents spécialisés
- Une mémoire structurée (SQLite) pour des capacités avancées
- Une architecture testable et observable
- Un système de logging complet pour le debugging

## 🏗️ Architecture

```
clara-v3/
├── agents/           # Agents spécialisés (orchestrateur, FS, Mail, Calendar, WhatsApp)
├── drivers/          # Drivers bas niveau pour l'accès aux services
├── memory/           # Système de mémoire (SQLite + futur index vectoriel)
├── config/           # Configuration (agents, settings, env)
├── logs/             # Logs structurés (session + debug)
├── ui/               # Interfaces utilisateur (chat + admin)
├── journal/          # Journal de développement
├── tests/            # Tests unitaires et d'intégration
└── run_clara.py      # Point d'entrée principal
```

## 🚀 Démarrage rapide

### Prérequis

- Python 3.8+
- pip

### Installation

```bash
# Cloner le repository
git clone https://github.com/mymy770/Clara.git
cd Clara

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp config/env.example .env
# Éditer .env avec vos clés API
```

### Lancement

```bash
python run_clara.py
```

## 📊 Roadmap

### ✅ Phase 0 - Infrastructure (En cours)
- [x] Structure du projet
- [x] Agents de base (squelettes)
- [x] Système de mémoire SQLite
- [x] Configuration YAML
- [ ] Tests unitaires de base

### 🔄 Phase 1 - Fondation Clara
- [ ] Orchestrateur Clara fonctionnel
- [ ] FS-Agent robuste (lire/écrire/lister/reporter)
- [ ] Logging structuré (2 fichiers par session)
- [ ] UI de chat reconnectée

### 📅 Phase 2 - Mémoire solide
- [ ] Schéma SQLite v1 complet
- [ ] API mémoire (CRUD)
- [ ] Intégration avec Clara (préférences, contacts, protocoles)
- [ ] Séparation court/moyen/long terme

### 🖥️ Phase 3 - UI Admin
- [ ] Interface admin minimale
- [ ] Visualisation des agents et états
- [ ] Accès aux logs (session + debug)
- [ ] Liste des sessions récentes

### 🔧 Phase 4 - Agents outils
- [ ] MailAgent + driver Gmail
- [ ] CalendarAgent + driver Calendar
- [ ] WhatsAppAgent + driver WhatsApp
- [ ] Tests réels pour chaque agent

### 🤖 Phase 5 - Automatisation avancée
- [ ] Protocoles et workflows multi-agents
- [ ] TODO list interne par mission
- [ ] Système de règles
- [ ] Index vectoriel (optionnel)

## 🧪 Tests

```bash
# Lancer tous les tests
python -m unittest discover tests

# Lancer un test spécifique
python -m unittest tests.test_fs_agent
```

## 📝 Logs

Clara génère deux types de logs par session :

1. **Session log** (`logs/sessions/<session_id>.session.json`) : Conversation humaine
2. **Debug log** (`logs/sessions/<session_id>.debug.json`) : Log technique complet

## 📚 Documentation

- Plan global du projet : `journal/dev_notes/2025-12-04_clara_v3_project_plan.md`
- Notes de développement : `journal/dev_notes/`

## 🤝 Contribution

Ce projet est en développement actif. Consultez le journal de développement pour suivre l'évolution.

## 📄 Licence

À définir

## 👤 Auteur

Jeremy Malai

## 🔗 Liens

- Repository GitHub : [https://github.com/mymy770/Clara](https://github.com/mymy770/Clara)
- Issues : [https://github.com/mymy770/Clara/issues](https://github.com/mymy770/Clara/issues)

---

**Note** : Ce projet est en phase de construction. Les fonctionnalités sont ajoutées progressivement selon la roadmap.

