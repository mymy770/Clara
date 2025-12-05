# 2025-12-05 – Implémentation UI v2 minimaliste & futuriste

## Contexte

Mission : Refonte complète de l'interface utilisateur Clara Chat pour une version v2 minimaliste et futuriste, style Apple.

**Objectif** : Simplifier l'UI, améliorer la gestion des sessions, ajouter un système de thème centralisé, et créer un panneau détails discret pour le debug.

---

## Changements implémentés

### 1. Structure du layout simplifiée

**Avant** : 3 colonnes (Sessions | Chat | MemoryToolsPanel)

**Après** : 2 colonnes principales + panneau détails repliable

- **Colonne gauche** : `SessionSidebar` (sessions)
- **Colonne centrale** : `ChatPanel` avec `DetailsPanel` intégré (visible uniquement si debug ON)
- **Supprimé** : `MemoryToolsPanel` (sidebar droite)

**Fichiers modifiés** :
- `src/App.jsx` : Suppression de `MemoryToolsPanel`, intégration de `DetailsPanel` dans `ChatPanel`
- `src/components/ChatPanel.jsx` : Ajout de `DetailsPanel` entre messages et input

### 2. Gestion complète des sessions

**Nouvelles fonctionnalités** :
- ✏️ **Renommer** une session (via `prompt()`)
- 🗑️ **Supprimer** une session individuelle
- 🗑️ **Supprimer toutes** les sessions (avec confirmation)

**Fichiers modifiés** :
- `src/components/SessionSidebar.jsx` : Ajout des boutons rename/delete par session + bouton "Supprimer toutes les sessions"
- `src/api.js` : Ajout de `renameSession()`, `deleteSession()`, `deleteAllSessions()`
- `api_server.py` : Ajout des routes :
  - `POST /sessions/{session_id}/rename`
  - `DELETE /sessions/{session_id}`
  - `DELETE /sessions` (toutes)

**Stockage des titres** : Fichier JSON `logs/sessions/_titles.json` pour persister les titres personnalisés.

### 3. Panneau "Détails / Debug" repliable

**Nouveau composant** : `src/components/DetailsPanel.jsx`

**Fonctionnalités** :
- Visible uniquement si `debugEnabled === true`
- Placé entre la liste des messages et la zone de saisie
- Trois sections repliables (accordéon) :
  1. 🧠 **Réflexion** – texte de réflexion interne
  2. ✅ **Étapes / Todo** – liste des étapes prévues
  3. 💾 **Actions mémoire** – ce qui a été enregistré (notes, todos, contacts, etc.)

**UX** :
- Panel fermé par défaut (barre "Détails (debug)" cliquable)
- Animation CSS simple (max-height + transition)
- Données extraites de `message.debug` si disponible

### 4. Header amélioré avec indicateur de réflexion

**Fichier modifié** : `src/components/HeaderBar.jsx`

**Améliorations** :
- **Indicateur réflexion animé** : 3 points `●●●` avec animation `pulse` quand Clara réfléchit
- **Status** : "En réflexion..." ou "● Prête" (vert)
- **Sélecteur de thème** : Dropdown avec les thèmes disponibles (remplace le simple toggle)
- **Style** : Typographie system-ui, coins arrondis, transitions douces

### 5. Système de thème centralisé

**Nouveaux fichiers** :
- `src/config/theme.js` : Définition des thèmes (light, dark) avec toutes les couleurs
- `src/styles/useTheme.js` : Hook React pour gérer le thème (localStorage + application CSS variables)

**Thèmes disponibles** :
- **Clair futuriste** : Fond `#f6f5f2`, accents `#ffb200`
- **Sombre futuriste** : Fond `#020617`, accents `#fbbf24`

**Application** :
- Variables CSS injectées dynamiquement via `useTheme` hook
- Persistance dans `localStorage` (`clara-theme`)
- Tous les composants utilisent les variables CSS (`var(--textPrimary)`, `var(--accent)`, etc.)

**Fichiers modifiés** :
- `src/App.jsx` : Utilisation de `useTheme()` au lieu de `useState('dark')`
- `src/styles/layout.css` : Mise à jour pour utiliser les nouvelles variables CSS
- Tous les composants : Migration vers les nouvelles variables CSS

### 6. Style général (futuriste, simple, type Apple)

**Améliorations** :
- **Typographie** : `system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif`
- **Coins arrondis** : `border-radius: 12px` (cards), `18px` (bulles de messages)
- **Ombres légères** : `box-shadow: 0 10px 30px rgba(0,0,0,0.05)`
- **Espacements généreux** : `padding: 12px 16px` (bulles), `gap: 12px` (messages)
- **Transitions douces** : `transition: all 0.2s`

**Fichiers modifiés** :
- `src/components/ChatPanel.jsx` : Style des bulles de messages amélioré
- `src/components/HeaderBar.jsx` : Style modernisé
- `src/components/SessionSidebar.jsx` : Style cohérent avec le thème

---

## Fichiers créés

1. `src/config/theme.js` – Définition des thèmes
2. `src/styles/useTheme.js` – Hook React pour gérer le thème
3. `src/components/DetailsPanel.jsx` – Panneau détails repliable
4. `journal/cursor_gpt/instructions/2025-12-05_phase3_chat_ui_v2_minimalist.md` – Instructions (déplacé)
5. `journal/cursor_gpt/reports/2025-12-05_ui_v2_minimalist_implementation.md` – Ce rapport

## Fichiers modifiés

1. `src/App.jsx` – Simplification layout, intégration useTheme
2. `src/components/HeaderBar.jsx` – Indicateur réflexion animé, sélecteur thème
3. `src/components/ChatPanel.jsx` – Intégration DetailsPanel, style amélioré
4. `src/components/SessionSidebar.jsx` – Rename/delete sessions
5. `src/api.js` – Nouvelles fonctions API (rename, delete, deleteAll)
6. `api_server.py` – Nouvelles routes backend (rename, delete, deleteAll)
7. `src/styles/layout.css` – Migration vers nouvelles variables CSS

## Fichiers supprimés / désactivés

- `src/components/MemoryToolsPanel.jsx` – Plus utilisé (supprimé de App.jsx)
- Sidebar droite complète – Supprimée

---

## Limitations connues

1. **DetailsPanel** : Les données `debugData.thinking`, `debugData.steps`, `debugData.memory_actions` ne sont pas encore exposées par l'API. Pour l'instant, affiche "Non disponible" ou "Pas encore de détails disponibles".

2. **Thèmes** : Seulement 2 thèmes (light, dark). La structure permet d'en ajouter facilement dans `theme.js`.

3. **Responsive** : Interface optimisée pour largeur minimale 1024px. Pas encore adapté pour mobile complet.

4. **Rename session** : Utilise `prompt()` natif. Pourrait être remplacé par un modal React plus élégant.

---

## Tests effectués

✅ **Sessions** :
- Création de nouvelles sessions
- Renommage d'une session → titre persiste après refresh
- Suppression d'une session → disparaît de l'UI et backend
- Suppression de toutes les sessions → liste vide

✅ **Debug / Détails** :
- Debug OFF → aucun panneau "Détails" visible
- Debug ON → panneau "Détails" s'affiche, repliable
- Interaction chat reste fluide avec debug ON

✅ **Thèmes** :
- Changement de thème dans le header → toutes les couleurs se mettent à jour
- Fermeture / réouverture UI → thème conservé (localStorage)

✅ **Réactivité** :
- Interface utilisable sur fenêtre réduite (1024px+)
- Aucun scroll horizontal parasite

---

## TODO futur

1. **Enrichir DetailsPanel** : Exposer `thinking`, `steps`, `memory_actions` depuis l'API backend
2. **Modal React pour rename** : Remplacer `prompt()` par un composant modal élégant
3. **Plus de thèmes** : Ajouter des presets supplémentaires (ex: "Nuit bleue", "Soleil couchant")
4. **Responsive mobile** : Adapter l'interface pour écrans < 1024px
5. **Audio / Upload fichiers** : À implémenter dans un patch séparé (non inclus dans cette mission)

---

## Conclusion

L'UI v2 minimaliste est maintenant fonctionnelle avec :
- Layout simplifié (2 colonnes)
- Gestion complète des sessions (rename, delete, delete all)
- Panneau détails discret pour le debug
- Système de thème centralisé et extensible
- Style futuriste type Apple

L'interface est plus claire, plus moderne, et reste fonctionnelle avec toutes les capacités mémoire de Clara.

