# 2025-12-05 – Implémentation UI v2 depuis legacy index.html

## Contexte

Mission : Recréer l'esprit et les fonctions de l'ancien `index.html` dans la nouvelle UI React, en gardant les endpoints backend actuels et en évitant tout code mort inutile.

**Objectif** : Recréer l'UI complète avec :
- Structure 3 colonnes (Sidebar | Chat | RightPanel)
- Gestion complète des sessions (rename inline, delete, delete all)
- Panneau droit avec Todo/Process/Think
- Système de thème complet avec panneau de réglage des couleurs
- Toutes les fonctionnalités de l'ancien HTML

---

## Changements implémentés

### 1. Organisation des fichiers

**Fichiers déplacés** :
- `gpt_cursor/index.html` → `ui/chat_frontend/legacy_ui/clara_legacy_index.html` (référence uniquement)
- `gpt_cursor/2025-12-05_patch_ui_v2_from_legacy_index.md` → `journal/cursor_gpt/instructions/`

### 2. Système de thème complet

**Nouveau fichier** : `src/config/themeManager.js`

**Fonctionnalités** :
- `loadThemeFromLocalStorage()` : Charge le thème depuis localStorage
- `saveThemeToLocalStorage(theme)` : Sauvegarde le thème
- `applyThemeToDocument(theme)` : Applique les variables CSS
- `initTheme()` : Initialise le thème au démarrage (avant rendu React)

**Variables CSS** : Toutes les variables de l'ancien HTML sont supportées :
- Sidebar (bg, text, border, footer)
- Header (bg, text, border)
- Chat (bg, text, time)
- Bulles (Jeremy et Clara : bg, border, text)
- Input (area, bg, text, border)
- Bouton Envoyer (bg, text, border)
- Panneau droit (bg, header, border)
- Boutons (Todo, Settings, Delete All)
- Think (bg, header, border, text)
- Taille police

**Fichiers modifiés** :
- `src/main.jsx` : Appel à `initTheme()` avant le rendu React
- `src/styles/global.css` : Variables CSS par défaut

### 3. Structure 3 colonnes

**Fichier modifié** : `src/App.jsx`

**Structure** :
- **Colonne gauche** : `SessionSidebarV2` (sessions)
- **Colonne centrale** : `ChatArea` (chat + header avec bouton Todo)
- **Colonne droite** : `RightPanel` (Todo/Process/Think)

**Layout** :
```jsx
<div style={{ display: 'flex', height: '100vh' }}>
  <SessionSidebarV2 />
  <div style={{ flex: 1 }}>
    <Header />
    <ChatArea />
  </div>
  <RightPanel />
</div>
```

### 4. SessionSidebarV2 améliorée

**Nouveau fichier** : `src/components/SessionSidebarV2.jsx`

**Fonctionnalités** :
- ✏️ **Rename inline** : Champ `<input>` qui remplace le titre, Enter pour valider, Escape ou blur pour annuler
- 🗑️ **Supprimer** une session avec modal de confirmation
- 🗑️ **Tout supprimer** avec modal de confirmation
- ⚙️ **Bouton Couleurs** pour ouvrir le panneau de réglage
- Auto-sélection de la première session si aucune n'est sélectionnée

**Composants intégrés** :
- `ConfirmModal` : Modal de confirmation pour suppressions
- `AppearanceSettings` : Panneau de réglage des couleurs

**Endpoints utilisés** :
- `GET /sessions` → liste
- `POST /sessions` → créer
- `GET /sessions/{id}` → détails + messages
- `POST /sessions/{id}/rename` → renommer
- `DELETE /sessions/{id}` → supprimer une
- `DELETE /sessions` → supprimer toutes

### 5. ChatArea

**Nouveau fichier** : `src/components/ChatArea.jsx`

**Fonctionnalités** :
- Affichage des messages (bulles Jeremy vs Clara)
- Formatage de l'heure (`formatTime`)
- Indicateur de saisie "Clara écrit..." (basé sur `isThinking`)
- Textarea multi-ligne avec `Enter` pour envoyer, `Shift+Enter` pour retour à la ligne
- Auto-resize du textarea
- Scroll automatique en bas à chaque update
- Appel au backend : `POST /chat` avec `{ message, session_id }`

**Style** : Utilise toutes les variables CSS du thème (bulles, input, bouton)

### 6. RightPanel (Todo/Process/Think)

**Nouveau fichier** : `src/components/RightPanel.jsx`

**Fonctionnalités** :

**Onglets Todo/Process** :
- **Todo** : Liste de tâches (checkbox disabled, texte, timestamp)
  - Endpoint : `GET /sessions/{id}/todos`
  - Fallback : `GET /sessions/{id}/logs` + filtrage `TODO` / `STEP`
- **Process** : Derniers logs (avec code couleur success / error)
  - Endpoint : `GET /sessions/{id}/logs`
  - Affiche les 20 derniers logs en reverse

**Section Think** :
- Flux de "pensées" avec phases (THINK, PLAN, OBSERVE, ERROR)
- Couleur de barre à gauche selon la phase
- Auto-scroll intelligent : uniquement si nouvelles pensées ET utilisateur était en bas
- Endpoint : `GET /sessions/{id}/thinking`

**Polling** : Toutes les 2 secondes (uniquement si session sélectionnée)

### 7. AppearanceSettings

**Nouveau fichier** : `src/components/AppearanceSettings.jsx`

**Fonctionnalités** :
- Panneau flottant (`position: absolute`) à droite
- Sections complètes : Sidebar, Header, Chat, Bulle Jeremy, Bulle Clara, Input, Boutons, Bande droite, Think, Footer
- Pour chaque item : label + `<input type="color">` (ou `number` pour taille police)
- **Preview en live** : Changements appliqués immédiatement via `applyThemeToDocument`
- **Boutons** :
  - `✓ Appliquer` → sauvegarde dans localStorage + ferme
  - `✕ Annuler` → restaure `originalTheme` et ferme
  - `Réinitialiser par défaut` → reset + sauvegarde

**Gestion d'état** :
- `originalTheme` sauvegardé à l'ouverture pour pouvoir annuler
- Tous les changements sont preview en live

### 8. Routes backend ajoutées

**Fichier modifié** : `api_server.py`

**Nouvelles routes** :
- `POST /sessions` : Crée une nouvelle session
- `GET /sessions/{session_id}/todos` : Récupère les todos (retourne `[]` pour l'instant)
- `GET /sessions/{session_id}/logs` : Récupère les logs depuis `logs/debug/{session_id}.json`
- `GET /sessions/{session_id}/thinking` : Récupère les thinking depuis `logs/debug/{session_id}.json`

**Fonctions API frontend** :
- `createSession()` : Crée une session
- `getSessionTodos(sessionId)` : Récupère les todos
- `getSessionLogs(sessionId)` : Récupère les logs
- `getSessionThinking(sessionId)` : Récupère les thinking

### 9. Composants utilitaires

**Nouveau fichier** : `src/components/ConfirmModal.jsx`

**Fonctionnalités** :
- Modal de confirmation réutilisable
- Message personnalisable
- Boutons "Annuler" et "Supprimer"
- Overlay cliquable pour fermer

---

## Fichiers créés

1. `ui/chat_frontend/legacy_ui/clara_legacy_index.html` – Référence (déplacé)
2. `src/config/themeManager.js` – Gestionnaire de thème
3. `src/styles/global.css` – Variables CSS globales
4. `src/components/ChatArea.jsx` – Zone de chat
5. `src/components/RightPanel.jsx` – Panneau droit (Todo/Process/Think)
6. `src/components/AppearanceSettings.jsx` – Panneau de réglage des couleurs
7. `src/components/SessionSidebarV2.jsx` – Sidebar sessions améliorée
8. `src/components/ConfirmModal.jsx` – Modal de confirmation
9. `journal/cursor_gpt/reports/2025-12-05_patch_ui_v2_from_legacy_index.md` – Ce rapport

## Fichiers modifiés

1. `src/App.jsx` – Restructuré en 3 colonnes
2. `src/main.jsx` – Initialisation du thème avant rendu
3. `src/api.js` – Ajout des fonctions `createSession`, `getSessionTodos`, `getSessionLogs`, `getSessionThinking`
4. `api_server.py` – Ajout des routes `/sessions` (POST), `/sessions/{id}/todos`, `/sessions/{id}/logs`, `/sessions/{id}/thinking`

## Fichiers supprimés / désactivés

- `src/components/ChatPanel.jsx` – Remplacé par `ChatArea.jsx`
- `src/components/HeaderBar.jsx` – Intégré dans `App.jsx`
- `src/components/SessionSidebar.jsx` – Remplacé par `SessionSidebarV2.jsx`
- `src/components/DetailsPanel.jsx` – Non utilisé dans cette version
- `src/components/MemoryToolsPanel.jsx` – Non utilisé dans cette version
- `src/components/DebugPanel.jsx` – Non utilisé dans cette version
- `src/styles/theme.css` – Remplacé par `global.css`
- `src/styles/useTheme.js` – Remplacé par `themeManager.js`
- `src/config/theme.js` – Remplacé par `themeManager.js`

---

## Limitations connues

1. **Todos** : L'endpoint `/sessions/{id}/todos` retourne une liste vide. À implémenter avec le système de todos de Clara.

2. **Logs/Thinking** : Les données sont lues depuis `logs/debug/{session_id}.json`. Le format doit correspondre à ce que génère `DebugLogger`.

3. **Format messages backend** : Le backend peut retourner soit `{ messages: [...] }` soit `{ reply: "..." }`. Le frontend gère les deux formats.

4. **Responsive** : Interface optimisée pour largeur minimale 1024px. Pas encore adapté pour mobile complet.

---

## Tests à réaliser

✅ **Sessions** :
- Créer plusieurs sessions, les renommer inline, les supprimer une par une
- Utiliser "Tout supprimer" et confirmer que tout est vidé (UI + backend)

✅ **Chat** :
- Envoyer plusieurs messages, vérifier l'ordre, les timestamps, le scroll auto
- Reprendre une session ancienne et vérifier que l'historique se charge correctement

✅ **Todo / Process / Think** :
- Lancer une demande complexe à Clara qui génère des todos et du thinking
- Vérifier mise à jour automatique des trois onglets pendant la conversation
- Vérifier que fermer / rouvrir le panneau garde l'état

✅ **Thème / Apparence** :
- Changer plusieurs couleurs dans le panel, appliquer → vérifier rendu
- Recharger la page → les couleurs doivent persister
- Tester "Annuler" et "Réinitialiser"

✅ **Résilience** :
- Que se passe-t-il si l'API `/todos` n'existe pas ? → La UI doit automatiquement tomber sur le parsing des logs, sans crash
- Si `/thinking` est vide → affichage d'un message neutre, pas d'erreur en console

---

## Conclusion

L'UI v2 est maintenant complètement implémentée avec :
- Structure 3 colonnes fonctionnelle
- Gestion complète des sessions (rename inline, delete, delete all)
- Panneau droit avec Todo/Process/Think et polling automatique
- Système de thème complet avec panneau de réglage des couleurs
- Toutes les fonctionnalités de l'ancien HTML recréées en React

L'interface est maintenant cohérente avec l'esprit de l'ancien `index.html`, tout en étant moderne et maintenable avec React.

