# 2025-12-05_patch_ui_v2_from_legacy_index.md

## Contexte

Jeremy a remis son ancien `index.html` (UI Clara 1) dans le même dossier que ce document).  
Ce fichier sert de **référence fonctionnelle et visuelle** : gestion des sessions à gauche, panneau Todo/Process/Think à droite, panneau de réglages de couleurs complet, etc.

La nouvelle UI est en React (Vite) dans `ui/chat_frontend/src`.  
Objectif : **recréer l’esprit et les fonctions de l’ancien `index.html` dans la nouvelle UI React**, en gardant les endpoints back actuels et en évitant tout code mort inutile.

> Important : ne pas tenter de rebrancher l’ancien HTML tel quel. Il faut **reprendre les idées** et les réimplémenter proprement en React + CSS variables.

---

## 1. Organisation des fichiers

Dans `ui/chat_frontend/src` :

- Garder : `main.jsx`, `api.js`, `App.jsx`, dossier `components/`, `styles/`, etc.
- Ajouter un sous‑dossier de référence (optionnel mais conseillé) :  
  - `ui/chat_frontend/legacy_ui/`  
    - y placer l’ancien `index.html` sous le nom `clara_legacy_index.html` (référence uniquement, pas utilisé au runtime).

Mettre dans le README de la UI une note courte : ce HTML sert juste de **spécification UX**.

---

## 2. Variables globales de thème (couleurs & tailles)

### 2.1. CSS variables

Dans le fichier de styles global (ex : `src/styles/global.css` ou équivalent) :

- Définir les mêmes variables CSS que dans l’ancien `index.html` (sidebar, header, chat, bulles, think, todo, footer, etc.).  
- Copier la **liste des variables** depuis le `<style>` du vieux `index.html` (section `:root { ... }`) et les adapter au fichier CSS global.

Ces variables doivent être appliquées à toutes les parties de la nouvelle UI (sidebar, header, chat, boutons, panneau de droite).

### 2.2. Gestion des couleurs côté JS

Créer un module utilitaire dans `src/config/theme.js` :

- Fonctions :
  - `loadThemeFromLocalStorage()`
  - `saveThemeToLocalStorage(theme)`
  - `applyThemeToDocument(theme)`

Le thème doit correspondre à la structure utilisée dans l’ancien HTML (mêmes clés que dans `localStorage.setItem('clara_colors', ...)`).

Au bootstrap de l’app (`main.jsx`) :

- Charger le thème depuis `localStorage` si disponible.
- Appliquer les CSS variables via `applyThemeToDocument` **avant** le rendu initial (pour éviter le “flash” de couleurs par défaut).

---

## 3. Structure générale de l’UI dans `App.jsx`

Recomposer `App.jsx` avec la structure 3 colonnes inspirée de l’ancien `index.html` :

1. **Sidebar gauche (sessions)**
2. **Zone centrale (chat)**
3. **Panneau droit (Todo / Process / Think)**

### 3.1. Sidebar gauche (sessions)

Fonctionnalités à reprendre exactement de l’ancien HTML :

- Liste des sessions avec :
  - titre (nom de fichier sans `.txt`)
  - survol / sélection
- Bouton `+ Nouvelle` pour créer une nouvelle session.
- Bouton ⚙️ en bas pour ouvrir le panneau de couleurs.
- Bouton `🗑️ Tout supprimer` pour supprimer toutes les sessions avec **popup de confirmation**.

Endpoints à utiliser (déjà existants) :

- `GET /sessions` → liste
- `POST /sessions` → créer
- `GET /sessions/{id}` → détails + messages
- `PATCH /sessions/{id}` → renommer (champ `title`)
- `DELETE /sessions/{id}` → supprimer une
- `DELETE` sur chacune en boucle pour “tout supprimer” (voir logique de l’ancien HTML).

Comportement :

- Renommage inline (champ `<input>` qui remplace le titre, Enter pour valider, Escape ou blur pour annuler).
- Suppression unitaire avec même popup de confirmation que “Tout supprimer”.
- Quand on supprime la session active :
  - nettoyer le chat
  - vider Todo/Process/Think
  - si d’autres sessions existent, sélectionner la première automatiquement.

### 3.2. Zone centrale (chat)

Composant principal : `<ChatArea />` (dans `components/ChatArea.jsx` par exemple).  
Fonctions :

- Affichage des messages, exactement comme `buildMessageElement` dans l’ancien HTML :
  - bulles Jeremy vs Clara
  - affichage de l’heure (`formatTime`).
- Indicateur de saisie “Clara écrit…” (basé sur `typing`).
- Textarea multi‑ligne avec `Enter` pour envoyer, `Shift+Enter` pour retour à la ligne.
- Appel au backend :
  - `POST /message` avec `{ message, session_id }`
  - Réponse contient `messages` + éventuellement `session_id` mis à jour.

Points importants :

- Après envoi :
  - afficher le message local de Jeremy instantanément
  - lancer le loader “Clara écrit…”
  - à la réponse → rerendre toute la liste des messages.
- Scroller automatiquement en bas à chaque update, comme dans l’ancien script (`scrollToBottom`).

### 3.3. Panneau droit (Todo / Process / Think)

Créer un composant `<RightPanel />` dans `components/RightPanel.jsx`.

Fonctions (à reprendre du vieux HTML) :

- Bouton `Todo` en haut à côté du titre Clara pour ouvrir/fermer le panneau.
- Dans le panneau :
  - Onglets ` Todo` et ` Process` (comme `right-tab`).
  - Section Todo : liste de tâches (checkbox disabled, texte, timestamp).
  - Section Process : derniers logs (avec code couleur success / error).  
  - Section Think : flux de “pensées” avec phases (THINK, PLAN, OBSERVE, ERROR) et couleur de barre à gauche.

Endpoints :

- Todo :  
  - essayer `GET /sessions/{id}/todos`  
  - si 404 ou erreur → fallback sur `GET /sessions/{id}/logs` + filtrage `TODO` / `STEP` comme dans `renderTodosFromLogs`.
- Process :  
  - `GET /sessions/{id}/logs`
- Think :  
  - `GET /sessions/{id}/thinking`

Comportement :

- Polling léger (toutes les 2–3 s max) sur logs + thinking **uniquement si une session est sélectionnée**.
- Respecter la logique de scroll de l’ancien HTML pour le panneau Think :
  - auto‑scroll uniquement si l’utilisateur est déjà proche du bas.

---

## 4. Panneau “Think” et Todo : mapping avec la nouvelle Clara

Dans la nouvelle version de Clara, on a déjà :

- un système de **thinking** (phases think/plan/observe/error_rethink)
- un système de **todos** dérivé des plans / process.

Adapter la logique de mapping :

- Pour chaque item `thinking` :  
  - reprendre `phase`, `text`, `ts` → même rendu que dans l’ancien HTML (`think-entry`, `think-phase`, `think-time`).
- Pour Todo :
  - si endpoint `/todos` : utiliser la structure renvoyée (texte, `created`, `done`).
  - sinon, parser les logs comme dans `renderTodosFromLogs`.

Ne JAMAIS bloquer Clara si `todos` ou `thinking` sont vides : juste afficher “Aucune tâche / réflexion pour le moment”.

---

## 5. Panneau de réglage des couleurs (UI Settings)

Créer un composant `<AppearanceSettings />` rendu dans `App.jsx` juste au‑dessus de la zone centrale, mais positionné comme dans l’ancien HTML :

- panel flottant (`position: absolute`) à droite, ouvert via le bouton ⚙️ de la sidebar.
- structure du panel et liste des couleurs → **reprendre la logique de `#settings-panel`** du vieux HTML :
  - sections Sidebar, Header, Chat, Bulle Jeremy, Bulle Clara, Input, Boutons, Bande droite, Think, Footer, etc.
  - pour chaque item : label + `<input type="color">` (et un numeric pour la taille de police).

Fonctionnement :

- Quand on ouvre le panel :
  - sauvegarder le thème courant dans un state `originalTheme` (pour pouvoir annuler).
- Lorsqu’on modifie un input :
  - appliquer les changements en live via `applyThemeToDocument` (preview).
- Boutons du panel :
  - `✓ Appliquer` → sauvegarder dans `localStorage` + fermer + mettre à jour `originalTheme`.
  - `✕ Annuler` → restaurer `originalTheme` et fermer.
  - `Réinitialiser par défaut` → reset + sauvegarde dans `localStorage`.

---

## 6. Suppression des éléments inutiles de la nouvelle UI actuelle

Dans la nouvelle version React, **supprimer ou désactiver** :

- le switch `Debug ON/OFF` et le soleil “dark/light mode” si encore présents.
- les boutons rapides “Voir mes notes / todos / process / protocols / préférences / contacts” à droite.
- les actions rapides “Reformuler / Résumer / Brainstorm” si elles sont juste des prompts statiques.
- les switches “Mode réflexion profonde / Sauvegarde auto notes / Utilisation auto mémoire” **tant qu’ils ne sont pas réellement branchés sur de la logique back**.

L’idée : garder l’interface **propre, minimaliste et orientée travail**, avec :
- Sidebar sessions + gestion complète
- Chat propre
- Panneau droit Todo/Process/Think
- Panneau de couleurs complet

Tout le reste viendra plus tard.

---

## 7. Tests à réaliser (checklist)

Après implémentation, vérifier manuellement :

1. **Sessions**
   - Créer 3 sessions, les renommer, les supprimer une par une.
   - Utiliser “Tout supprimer” et confirmer que tout est vidé (UI + backend).

2. **Chat**
   - Envoyer plusieurs messages, vérifier l’ordre, les timestamps, le scroll auto.
   - Reprendre une session ancienne et vérifier que l’historique se charge correctement.

3. **Todo / Process / Think**
   - Lancer une demande complexe à Clara qui génère des todos et du thinking.
   - Vérifier mise à jour automatique des trois onglets pendant la conversation.
   - Vérifier que fermer / rouvrir le panneau garde l’état.

4. **Thème / Apparence**
   - Changer plusieurs couleurs dans le panel, appliquer → vérifier rendu.
   - Recharger la page → les couleurs doivent persister.
   - Tester “Annuler” et “Réinitialiser”.

5. **Résilience**
   - Que se passe‑t‑il si l’API `/todos` n’existe pas ?
     - La UI doit automatiquement tomber sur le parsing des logs, sans crash.
   - Si `/thinking` est vide → affichage d’un message neutre, pas d’erreur en console.

---

## 8. Résumé pour toi, Cursor

1. Utilise `ui/chat_frontend/index.html` fourni par Jeremy comme **spécification** de l’UI (structure + styles + comportement), pas comme fichier servi.
2. Recrée cette UI en React dans `src/App.jsx` + composants (`ChatArea`, `RightPanel`, `AppearanceSettings`, etc.) en t’appuyant sur les endpoints déjà fonctionnels.
3. Implémente le système de thème par CSS variables + `localStorage` comme dans l’ancien fichier.
4. Nettoie les anciens éléments de la nouvelle UI qui ne sont plus cohérents (debug switch, quick actions, etc.).
5. Quand tu as fini, fais un **rapport de ce qui a été implémenté** et liste les éventuelles limitations restantes.
