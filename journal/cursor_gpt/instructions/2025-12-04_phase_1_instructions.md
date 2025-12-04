# 🚀 Phase 1 – Instructions de construction de l’infrastructure Clara (Cursor)

## 0. Objectif
Mettre en place la base minimale de Clara : orchestrator, driver LLM, settings, mémoire vide, logs structurés.
Aucune logique métier. Aucune action. Aucune toolchain.
Juste l’ossature propre qui permettra les phases suivantes.

## 1. Fichiers à implémenter

### 1️⃣ run_clara.py
- Point d’entrée de Clara.
- Charge settings.yaml
- Initialise Orchestrator
- Ouvre une nouvelle session (génère session_id)
- Boucle : input utilisateur → orchestrator.handle_message()
- Affiche la réponse
- Écrit deux logs :
  - logs/sessions/<session_id>.txt → transcript humain
  - logs/debug/<session_id>.json → debug complet (prompt envoyé, réponse brute, erreurs)

### 2️⃣ agents/orchestrator.py
- Construire le prompt complet (system + instructions projet + historique)
- Déterminer la langue de réponse
- Appeler LLMDriver.generate()
- Retourner la réponse textuelle
- Gérer l’historique récent (max 20 messages)
- Appeler LoggerDebug

### 3️⃣ drivers/llm_driver.py
- Lire config/settings.yaml
- Appeler OpenAI (modèle gpt-5.1)
- Retourner :
  - texte LLM
  - usage (tokens)

### 4️⃣ config/settings.yaml
model: gpt-5.1
temperature: 0.7
max_tokens: 4096
language_policy: auto

### 5️⃣ memory/memory_core.py
Placeholder minimal :
- init_db()
- save_interaction()
- load_context()

### 6️⃣ logs/
Création des writers :
- logs/sessions/<id>.txt (humain)
- logs/debug/<id>.json (debug complet : input, prompt, raw_response, erreurs)

### 7️⃣ tests/
Créer fichiers vides :
- test_orchestrator.py
- test_llm_driver.py
- test_run_clara.py

### 8️⃣ Discipline développement
- Commit : "Phase 1 – Clara infrastructure skeleton"
- Push sur main
- Archiver ce fichier dans journal/cursor_gpt/

# ✅ FIN
