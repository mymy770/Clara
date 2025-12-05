# 2025-12-05 – Phase 3 UI Remix (Ancienne UI + Nouvelle UI)

## Objectif

Adapter l’UI React actuelle (`ui/chat_frontend`) pour :
- Reprendre **toutes les fonctionnalités utiles** de l’ancienne interface (`index_old.html`)
- Garder le **style futuriste / clean** de la nouvelle UI React
- Rendre l’UI **hautement configurable** (couleurs + layout)
- Préparer l’UI à l’arrivée des futurs agents / outils

Tu travailles **uniquement** dans le dossier :

- `ui/chat_frontend/`

Le backend (FastAPI, orchestrator, mémoire, etc.) **ne doit pas être modifié** dans ce patch.

---

## 1. Architecture et fichiers

### 1.1. Garder la structure React existante

Conserver la structure actuelle :

- `ui/chat_frontend/src/App.jsx`
- `ui/chat_frontend/src/main.jsx`
- `ui/chat_frontend/src/api.js`
- `ui/chat_frontend/src/components/*`
- `ui/chat_frontend/src/styles/*`
- `ui/chat_frontend/src/config/*`

Tu peux **ajouter** des composants / fichiers si nécessaire, mais pas tout casser.
On veut rester sur un front React moderne (Vite).

### 1.2. Fichiers de config à créer / compléter

1. `ui/chat_frontend/src/config/theme.json`
   - Sert à piloter **toutes les couleurs principales** de l’UI.
   - Exemple de structure :

```jsonc
{
  "themeName": "clara-default",
  "colors": {
    "background": "#050816",
    "backgroundAlt": "#090f1f",
    "panel": "#0b1020",
    "accent": "#4f46e5",
    "accentSoft": "#6366f1",
    "danger": "#f97373",
    "textPrimary": "#f9fafb",
    "textSecondary": "#9ca3af",
    "border": "rgba(148, 163, 184, 0.4)",
    "glow": "rgba(79, 70, 229, 0.5)"
  },
  "radii": {
    "panel": "18px",
    "button": "999px"
  }
}
```

2. `ui/chat_frontend/src/styles/theme.css`
   - Expose les valeurs de `theme.json` sous forme de **CSS variables**.
   - Tu peux hardcoder un premier thème, mais il doit être facile à alimenter ensuite depuis `theme.json`.

3. `ui/chat_frontend/src/config/layout.json`
   - Décrit la **disposition des panneaux** (gauche / centre / droite).
   - Exemple de structure simple :

```jsonc
{
  "layout": {
    "sidebarLeftWidth": 280,
    "sidebarRightWidth": 320,
    "showRightPanel": true,
    "showSessions": true,
    "showMemoryPanel": true
  }
}
```

L’objectif : que Jeremy puisse, plus tard, modifier **couleurs + layout** sans toucher directement au code React.

---

## 2. Structure visuelle cible (mix ancienne + nouvelle UI)

On veut retrouver la logique visuelle de `index_old.html`, mais en version React moderne.

### 2.1. Layout général (3 colonnes)

Dans `App.jsx`, mettre en place un layout **3 colonnes** :

- **Colonne gauche – Sessions**
  - Liste des sessions (id, titre, date)
  - Bouton « Nouvelle session »
  - Icône pour dupliquer / renommer / supprimer
  - Barre de recherche des sessions
  - Petite pastille d’état (ex : active / pinned)

- **Colonne centrale – Chat principal**
  - Header minimal avec : nom « Clara », état (🟢 / 🟡), éventuellement le modèle utilisé.
  - Flux de messages (toi vs Clara)
  - Indicateur de « thinking » / activité
  - Barre d’input avec :
    - champ texte
    - bouton envoyer
    - boutons de **quick actions** (voir plus bas)

- **Colonne droite – Panneau intelligent**
  - Inspirée de la colonne droite de `index_old.html`
  - Onglets ou sections :
    - **Mémoire** : notes / todos / process / protocols / preferences / contacts (vue compacte)
    - **Modes & options** : toggles pour guiding, use_memory, auto_save_notes, etc.
    - **Actions rapides** : boutons type « Résumer », « Lister les todos », « Montrer mes protocoles », etc.

Le layout doit être **responsive**, mais priorité au desktop pour l’instant.

---

## 3. Fonctionnalités à reprendre de l’ancienne UI

À partir de `index_old.html`, réintégrer dans la nouvelle UI les éléments suivants, en les adaptant à la nouvelle Clara :

### 3.1. Panneau droit – Mémoire & outils

Dans la colonne droite, créer un composant (par exemple `MemoryToolsPanel.jsx`) qui expose :

1. **Section Mémoire**
   - Boutons / liens pour :
     - « Voir mes notes »
     - « Voir mes todos »
     - « Voir mes process »
     - « Voir mes protocoles »
     - « Voir mes préférences »
     - « Voir mes contacts »
   - Chaque bouton envoie un message spécial au backend du type :
     - `command: "list_memory", type: "note" | "todo" | "process" | "protocol" | "preference" | "contact"`
   - Pour l’instant, tu peux simplement appeler l’endpoint chat avec un message système ou user explicite (ex : `"[SYS] LIST_NOTES"`), **sans changer la logique backend**.

2. **Section Quick actions**
   - Boutons comme dans l’ancienne UI :
     - « Reformuler »
     - « Résumer »
     - « Brainstorm »
     - etc.
   - Ces boutons pré-remplissent l’input ou envoient directement des templates de prompts.

3. **Section Modes**
   - Toggles simples gérés **côté front uniquement pour l’instant** :
     - `deepThinking` (ex : « Mode réflexion profonde »)
     - `autoSaveNotes`
     - `autoUseMemory`
   - Ces states sont juste conservés dans React et **peuvent être ajoutés au payload envoyé à l’API** sous un champ `meta`, sans casser l’existant (le backend peut les ignorer pour l’instant).

### 3.2. Boutons Note / Todo / Process / Protocol dans le chat

Dans la barre d’input du chat, ajouter des **petits boutons** qui :

- Préparent une commande structurée pour Clara, par exemple :
  - « Créer une note » → pré-remplit : `Crée une note : ...`
  - « Todo » → `Ajoute un todo : ...`
  - « Process » → `Crée un process structuré pour : ...`
  - « Protocol » → `Crée un protocole pour : ...`

Pas de magie : c’est juste du **convenience UX** pour l’utilisateur.

---

## 4. Personnalisation avancée (couleurs + layout)

### 4.1. Couleurs

- Tous les composants doivent utiliser **les variables CSS** définies dans `theme.css` :
  - `var(--bg-main)`
  - `var(--bg-panel)`
  - `var(--accent)`
  - `var(--text-primary)`
  - `var(--text-secondary)`
  - etc.

- Tu peux mapper ces variables aux valeurs de `theme.json` (aujourd’hui en dur si besoin).

Objectif : Jeremy doit pouvoir changer l’ambiance en modifiant **uniquement** `theme.json` + `theme.css`.

### 4.2. Layout configurable

- Lire `layout.json` au démarrage (ou importer un objet JS équivalent)
- Utiliser ses valeurs pour :
  - Largeur des sidebars
  - Afficher / masquer le panneau droit
  - Afficher / masquer la colonne sessions

Tu peux, en plus, prévoir un petit menu dans l’UI (ex : bouton « Layout » en haut à droite) qui permet de :
- Basculer entre 2–3 presets (ex : `full-focus`, `with-right-panel`, `minimal`)
- Ces presets peuvent être codés en dur pour l’instant.

Pas besoin d’un vrai drag & drop pour le moment, mais le code doit être écrit **proprement** pour qu’on puisse y revenir plus tard.

---

## 5. Intégration API (sans casser l’existant)

### 5.1. Appels API

- **Ne change pas** les endpoints définis dans la phase précédente (`api_server.py`).
- `api.js` doit toujours : 
  - récupérer la liste des sessions,
  - envoyer des messages,
  - récupérer l’historique d’une session.

### 5.2. Meta facultatif

Quand tu envoies un message, tu peux ajouter un champ optionnel :

```jsonc
{
  "session_id": "...",
  "message": "...",
  "meta": {
    "deepThinking": true,
    "autoSaveNotes": true,
    "autoUseMemory": true
  }
}
```

Le backend peut l’ignorer pour l’instant, mais au moins l’UI est prête.

---

## 6. Style et UX

### 6.1. Style visuel

- Garder le côté futuriste de la nouvelle UI (glow, panels arrondis, légers gradients)
- S’inspirer des éléments réussi de `index_old.html` :
  - Cartes translucides
  - Séparateurs propres
  - Icônes / labels clairs pour les sections

### 6.2. Ergonomie

- Tout doit rester **cliquable au clavier** (tab-friendly)
- Les états doivent être clairs :
  - session sélectionnée,
  - bouton actif / inactif,
  - toggle ON/OFF,
  - message en cours d’envoi / en attente de réponse.

---

## 7. Tests à faire avant de me rendre la main

1. Lancer l’API Clara (comme déjà défini).
2. Lancer le front :
   - `cd ui/chat_frontend`
   - `npm install` (si pas déjà fait)
   - `npm run dev`
3. Vérifier : 
   - ✅ Affichage des 3 colonnes
   - ✅ Navigation entre plusieurs sessions
   - ✅ Envoi d’un message simple → réponse de Clara
   - ✅ Boutons Note / Todo / Process / Protocol : pré-remplissent bien l’input
   - ✅ Les boutons Mémoire (notes, todos, process, protocols, preferences, contacts) envoient bien des requêtes (même si la réponse est encore brute)
   - ✅ Toggling des options (deepThinking, autoSaveNotes, autoUseMemory) modifie bien l’état dans React
   - ✅ Changement manuel des couleurs dans `theme.css` a un effet visible

Documente ensuite ce que tu as fait dans un fichier :  
`journal/dev_notes/2025-12-05_phase3_ui_remix.md`

Avec :
- Contexte
- Fichiers créés / modifiés
- Limitations / TODO éventuels
