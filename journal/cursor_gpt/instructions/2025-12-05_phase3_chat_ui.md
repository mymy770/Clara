# 2025-12-05 – Phase 3 : UI Chat Clara (Patch instructions for Cursor)

## 1. Contexte et contraintes

Projet : **Clara** (multi‑agents, mémoire, orchestrateur déjà en place).  
Phase 2 (mémoire + contacts + préférences) : **validée et stable**.  
Objectif de ce patch : ajouter une **UI de chat moderne** + une **API HTTP légère** SANS casser ce qui existe.

### Contraintes générales

- **NE PAS** modifier la logique mémoire existante :
  - `memory/schema.sql`
  - `memory/memory_core.py`
  - `memory/helpers.py`
  - `memory/contacts.py`
- **NE PAS** casser `run_clara.py` (mode terminal doit continuer à fonctionner comme aujourd’hui).
- Respecter la discipline de journaux :
  - Nouveau journal à créer : `journal/cursor_gpt/2025-12-05_phase3_chat_ui.md`
- Tous les changements doivent être **commités** proprement (un commit clair pour ce patch).

---

## 2. Backend – API HTTP minimale pour Clara

On garde `run_clara.py` pour le terminal, et on ajoute **un petit serveur HTTP** qui expose Clara à l’UI.

### 2.1. Nouveau fichier : `api_server.py` (à la racine du repo)

Implémenter un serveur **FastAPI** avec :

- Endpoint `GET /health`
  - Répond `{ "status": "ok" }`
- Endpoint `POST /chat`
  - Body JSON :
    ```json
    {
      "message": "texte utilisateur",
      "session_id": "optionnel",
      "debug": true
    }
    ```
  - Comportement :
    - Si `session_id` absent → créer une **nouvelle session** (comme `run_clara.py` le fait aujourd’hui).
    - Appeler la même logique que le terminal (orchestrateur) pour obtenir la réponse de Clara.
    - S’assurer que les logs de session sont bien écrits dans `logs/sessions/` comme en mode terminal.
  - Réponse JSON :
    ```json
    {
      "reply": "réponse texte de Clara",
      "session_id": "id_de_session",
      "debug": { ... }   // seulement si debug=true
    }
    ```
    - `debug` peut contenir par exemple : intents détectés, actions mémoire, tags générés.

- Endpoint `GET /sessions`
  - Retourne la liste des sessions existantes basées sur le contenu de `logs/sessions/`.
  - Format simple :
    ```json
    [
      { "session_id": "session_20251205_140416", "started_at": "...", "title": "optionnel" },
      ...
    ]
    ```

- Endpoint `GET /sessions/{session_id}`
  - Retourne l’historique brut de la session (contenu du fichier JSON de session déjà existant), ou un format simplifié :
    ```json
    {
      "session_id": "...",
      "messages": [
        { "role": "user", "content": "..." },
        { "role": "assistant", "content": "..." }
      ]
    }
    ```

> Important : réutiliser le plus possible le code déjà présent dans `run_clara.py` / `agents/orchestrator.py` pour éviter la duplication de logique.

### 2.2. Configuration & dépendances

- Mettre à jour `requirements.txt` pour ajouter :
  - `fastapi`
  - `uvicorn`
- Ajouter dans `README.md` une section :
  - Comment lancer le serveur API :
    ```bash
    uvicorn api_server:app --reload --port 8001
    ```
  - Comment lancer la UI (voir section UI ci‑dessous).

---

## 3. Frontend – UI Chat futuriste, simple, themable

L’UI de chat doit vivre dans :

- `ui/chat_frontend/`

Le but ici est une **V1 propre**, pas un monstre. Mais avec une **base de design solide**, facilement personnalisable.

### 3.1. Stack minimale

- Tu peux utiliser soit :
  - **Option A (recommandée)** : React + Vite dans `ui/chat_frontend/`
  - **Option B (plus simple)** : HTML + JS vanilla + bundler minimal
- Le plus important : **code clair, simple, structuré**.

### 3.2. Structure minimale

Dans `ui/chat_frontend/`, on veut au final quelque chose comme :

- `index.html`
- `src/`
  - `main.tsx` ou `main.js`
  - `App.tsx` / `App.jsx`
  - `components/`
    - `ChatPanel.tsx`
    - `SessionSidebar.tsx`
    - `DebugPanel.tsx`
    - `HeaderBar.tsx`
  - `styles/`
    - `theme.css`
    - `layout.css`
  - `config/`
    - `layout.json`  (voir plus bas)

Tu es libre d’ajuster les noms de fichiers, mais garde cette séparation **composants / styles / config**.

### 3.3. Design & theming

Objectifs design :
- **Futuriste**, **simple**, **épuré**.
- Très facile à **re-thémer** (changer toutes les couleurs sans toucher le code).

Implémentation demandée :

1. Dans `styles/theme.css`, définir tous les **tokens de design** via des **CSS variables** :

   ```css
   :root {
     --bg-main: #05060a;
     --bg-elevated: #0b0d12;
     --bg-soft: #11141c;

     --accent: #4f46e5;
     --accent-soft: #312e81;

     --text-main: #f9fafb;
     --text-muted: #9ca3af;

     --border-subtle: #1f2933;

     --radius-lg: 18px;
     --radius-md: 12px;
     --radius-sm: 8px;

     --shadow-soft: 0 18px 45px rgba(0,0,0,0.5);

     --font-sans: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
   }
   ```

2. Tous les composants UI doivent **uniquement** utiliser ces variables (pas de couleurs en dur).  
   Exemple :
   ```css
   .app-root {
     background: radial-gradient(circle at top, var(--accent-soft) 0, var(--bg-main) 45%);
     color: var(--text-main);
     font-family: var(--font-sans);
   }
   ```

3. Ajouter une **petite barre de contrôle des thèmes** (dans `HeaderBar`), même si pour l’instant elle ne fait que basculer entre 2 sets de variables (`:root.light` / `:root.dark` par exemple).  
   - But : que l’utilisateur puisse changer de thème facilement plus tard.  
   - Tu peux simplement ajouter une classe sur `<body>` et définir `.theme-light` / `.theme-dark` dans `theme.css`.

### 3.4. Layout configurable

Jeremy veut pouvoir **bouger les blocs** et organiser l’écran comme il veut **sans recoder**.

Pour la V1, on ne va pas coder un éditeur drag‑and‑drop complet, mais on va préparer une base **configurable par fichier** :

1. Créer un fichier `ui/chat_frontend/config/layout.json` qui décrit la disposition :

   ```json
   {
     "showLeftSidebar": true,
     "showRightDebug": true,
     "leftSidebarWidth": "280px",
     "rightSidebarWidth": "340px",
     "chatMinWidth": "480px"
   }
   ```

2. Dans `App` (ou composant racine), lire ce JSON au démarrage (import statique ou fetch local) et appliquer ces réglages dans le layout CSS (CSS Grid ou Flex).

3. Layout recommandé (en CSS grid) :
   - Colonne gauche : sessions
   - Centre : chat
   - Colonne droite : debug (optionnelle)
   - En-dessous : input de message collé en bas.

**Important :**  
Même si pour l’instant le changement de layout se fait en éditant `layout.json` à la main, la structure doit être pensée pour supporter plus tard :
- taille des panneaux configurable,
- panels activables/désactivables,
- éventuellement un mode “focus” (chat plein écran).

### 3.5. Fonctionnalités UI côté utilisateur

Dans la V1, l’UI doit permettre :

1. **Envoyer un message** à Clara
   - Champ texte + bouton “Envoyer”
   - `Enter` pour envoyer, `Shift+Enter` pour aller à la ligne
   - Appel à `POST /chat` avec `session_id` courant (ou sans pour créer une nouvelle session).

2. **Voir la conversation** :
   - Messages affichés en bulles ou blocs :
     - Alignement gauche pour l’utilisateur
     - Alignement droit (ou différent style) pour Clara
   - Afficher aussi **l’heure** du message si accessible (sinon la générer côté frontend).

3. **Gérer les sessions** (sidebar gauche) :
   - Liste des sessions (depuis `GET /sessions`).
   - Cliquer sur une session → charger ses messages (`GET /sessions/{id}`) et les afficher dans le chat.
   - Bouton “Nouvelle session” → réinitialise le chat et laisse le backend créer une nouvelle `session_id` au prochain `POST /chat`.

4. **Debug panel** (sidebar droite) :
   - Un toggle “Debug” dans le header.
   - Si activé → on appelle `POST /chat` avec `"debug": true` et on affiche la section `debug` de la réponse :
     - intents
     - type de mémoire utilisé
     - actions exécutées
     - etc. (Libre, selon ce que renvoie l’API)
   - Affichage en JSON formaté ou listes simples.

---

## 4. Intégration avec l’orchestrateur et la mémoire

### 4.1. Côté backend

- Le backend doit **absolument** passer par le même orchestrateur que `run_clara.py`.
- Les actions mémoire (notes, todos, contacts, préférences, etc.) doivent fonctionner **exactement comme en mode terminal**.
- Pour les réponses de debug :
  - Tu peux adapter l’orchestrateur (ou un wrapper) pour renvoyer une structure contenant :  
    - `raw_intent`  
    - `parsed_memory_action`  
    - `tags`  
    - etc.

### 4.2. Côté frontend

- Ne pas interpréter la logique métier, juste :
  - Afficher le texte utilisateur et le texte de Clara.
  - Afficher le debug si présent.
- Encapsuler les appels HTTP dans un petit module (par ex. `api.ts` / `api.js`) avec des fonctions :
  - `sendMessage(message, sessionId, debug)`
  - `listSessions()`
  - `loadSession(sessionId)`

---

## 5. Journaux et documentation

### 5.1. Journal à créer / compléter

Créer le fichier :  
`journal/cursor_gpt/2025-12-05_phase3_chat_ui.md` avec :

- Contexte (Phase 3 UI)
- Fichiers créés : `api_server.py`, contenu de `ui/chat_frontend/`, changements de `requirements.txt`, etc.
- Décisions techniques (FastAPI, layout JSON, thème CSS variables)
- Points à revoir plus tard (drag & drop de layout, thèmes multiples, etc.)

### 5.2. README

Mettre à jour `README.md` pour ajouter :

1. **Lancement en terminal** (déjà existant, garder) :
   ```bash
   python3 run_clara.py
   ```

2. **Lancement API + UI** :
   ```bash
   # Terminal 1 : API
   uvicorn api_server:app --reload --port 8001

   # Terminal 2 : UI (exemple si Vite)
   cd ui/chat_frontend
   npm install
   npm run dev
   ```

3. URL d’accès à l’UI (par ex. `http://localhost:5173` ou autre suivant la stack).

---

## 6. Tests à effectuer avant commit

1. API :
   - Lancer : `uvicorn api_server:app --reload --port 8001`
   - Tester à la main avec `curl` ou `httpie` :
     - `GET /health` → OK
     - `POST /chat` → Clara répond bien, nouvelle session créée.
2. UI :
   - Lancer le dev server de la UI.
   - Vérifier :
     - Envoi de message → réponse de Clara affichée.
     - Nouvelle session → fonctionne.
     - Liste des sessions → affichée.
     - Toggle Debug → affiche bien les infos de debug.
3. Vérifier que `run_clara.py` fonctionne **exactement comme avant**.
4. Vérifier qu’aucun fichier sensible (.env) n’est impacté.

---

## 7. Résumé final pour toi (Cursor)

1. Ajouter `api_server.py` (FastAPI) qui wrappe Clara et expose `/chat`, `/sessions`, `/sessions/{id}`, `/health`.
2. Mettre à jour `requirements.txt` et `README.md` pour documenter API + UI.
3. Construire une UI de chat dans `ui/chat_frontend/` :
   - Futuriste, simple, épurée.
   - Complètement themable via `styles/theme.css` (CSS variables).
   - Layout configurable via `config/layout.json` (sidebar gauche, chat, debug).
4. Intégrer la gestion des sessions (liste, sélection, nouvelle).
5. Ajouter un panneau debug optionnel basé sur le champ `debug` de la réponse API.
6. Documenter tout cela dans `journal/cursor_gpt/2025-12-05_phase3_chat_ui.md`.
7. Faire un **seul commit propre** pour ce patch.

Merci de confirmer dans le journal que tout a été testé (API, UI, mode terminal) avant push.
