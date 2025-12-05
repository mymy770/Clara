# 2025-12-05 – Patch UI v2 minimaliste & futuriste (Clara Chat)

## Contexte

Le chat frontend tourne avec Vite + React dans `ui/chat_frontend/`.  
La V1 fonctionne mais :
- sidebar droite peu utile (Mémoire / Actions rapides / Modes)
- peu de contrôle sur les couleurs (juste light/dark)
- pas de gestion des sessions (rename / delete / delete all)
- debug peu clair (bouton Debug ON/OFF sans vrai rôle)
- l’interface doit rester simple, futuriste, style Apple.

**Objectif de ce patch** :  
UI v2 = même backend, même API, mais :
1. Layout plus clean (2 colonnes principales + panneau détails repliable).
2. Gestion complète des sessions (renommer / supprimer / tout supprimer).
3. Panneau “détails” pour réflexion / actions / debug, discret.
4. Système de thème centralisé, avec quelques presets modifiables facilement.
5. Pas d’audio ni upload de fichiers dans ce patch (viendra dans un patch séparé).

---

## 1. Structure générale du layout

### 1.1. Organisation en 2 colonnes + panneau détails

Dans `src/App.jsx` (ou le composant racine qui gère le layout) :

- Conserver la colonne gauche **Sessions**.
- Conserver la colonne centrale **Chat**.
- **Supprimer la grande sidebar droite actuelle** (Mémoire, Actions rapides, Modes).
- Ajouter en bas de la zone de chat un **panneau “Détails” repliable**, qui n’apparaît **que si le debug est ON**.

Pseudo-structure :

```jsx
<AppLayout>
  <SidebarSessions />   {/* colonne gauche */}
  <MainChatArea>        {/* zone centrale */}
    <ChatHeader />      {/* Clara, modèle, status, debug toggle, thème */}
    <MessagesList />
    <DetailsPanel />    {/* repliable, visible seulement si debug === true */}
    <Composer />        {/* zone de saisie */}
  </MainChatArea>
</AppLayout>
```

Si ces composants n’existent pas encore, crée-les dans `src/components/` et adapte l’import.

---

## 2. Sessions : renommer, supprimer, tout supprimer

Fichiers concernés (à adapter selon le code actuel) :
- `src/components/SidebarSessions.jsx` (ou équivalent)
- éventuellement `src/api.js` pour les appels backend

### 2.1. Par session : rename + delete

Pour chaque session dans la liste :
- Afficher le titre + date comme aujourd’hui.
- Ajouter deux petites actions à droite (icônes ou boutons minimalistes) :
  - ✏️ **Renommer**
  - 🗑️ **Supprimer**

Exemple JSX simplifié :

```jsx
<li className={...}>
  <button onClick={() => onSelect(session.id)} className="session-main">
    <div className="session-title">{session.title || 'Session sans titre'}</div>
    <div className="session-meta">{formattedDate}</div>
  </button>
  <div className="session-actions">
    <button onClick={() => handleRename(session)}>✏️</button>
    <button onClick={() => handleDelete(session.id)}>🗑️</button>
  </div>
</li>
```

**Rename** :  
- Ouvrir un petit `prompt()` ou un mini modal React.
- Appeler une fonction `api.renameSession(session.id, newTitle)` si le backend la supporte.
- Sinon, **implémenter cette route côté backend** de façon minimale (voir plus bas).

**Delete** :  
- Appeler `api.deleteSession(session.id)`.
- Mettre à jour la liste côté frontend.

### 2.2. Bouton “Supprimer toutes les sessions”

En dessous du bouton `+ Nouvelle session`, ajouter un bouton texte discret :
- Label : `Supprimer toutes les sessions`
- Confirmation : `window.confirm('Supprimer toutes les sessions ? Cette action est définitive.')`
- Appel API : `api.deleteAllSessions()` (route à créer si elle n’existe pas).

### 2.3. Backend (si nécessaire)

Dans `api_server.py` (ou équivalent) :

- Vérifier s’il existe déjà des routes pour :
  - lister les sessions
  - créer une session
  - supprimer une session
- Si **rename** manque, ajouter une route simple, ex :

```python
@app.post("/sessions/{session_id}/rename")
def rename_session(session_id: str, payload: RenamePayload):
    # Mettre à jour le titre dans la structure de stockage actuelle
```

- Si **delete all** manque, ajouter :

```python
@app.delete("/sessions")
def delete_all_sessions():
    # Supprimer toutes les sessions stockées
```

Adapter au mode de persistence actuel (fichier JSON, SQLite, etc.).

---

## 3. Panneau “Détails / Debug” repliable

Objectif : garder la transparence sur ce que fait Clara, **sans polluer l’UI**.

### 3.1. État Debug global

Dans `App.jsx` ou un contexte global `ChatContext` :

- Garder un booléen `debugEnabled`.
- Le relier au bouton `Debug ON/OFF` dans le header (voir section 4).

### 3.2. Nouveau composant `DetailsPanel`

Créer `src/components/DetailsPanel.jsx` :

- Visible uniquement si `debugEnabled === true`.
- Placé **entre** la liste des messages et la zone de saisie.

Le panel contient **trois sections repliables** (accordéon simple) :
1. 🧠 **Réflexion** – texte de réflexion interne si on l’expose (optionnel, sinon “Non disponible”).
2. ✅ **Étapes / Todo** – liste des étapes prévues / en cours (si exposé par l’API).
3. 💾 **Actions mémoire** – ce qu’elle a enregistré pendant ce tour (notes, todos, contacts, etc.).

Les données viennent idéalement du backend :  
si l’API renvoie déjà une structure “debug” (JSON avec `thinking`, `actions`, etc.), l’utiliser.  
Sinon, afficher un message neutre : `Pas encore de détails disponibles pour ce message.`

UX :
- Panel fermé par défaut (juste une barre `Détails (debug)` cliquable).
- Cliquer ouvre/ferme avec une petite animation CSS simple (max-height + transition).

---

## 4. Header Clara + indicateur de réflexion

Fichier : `src/components/ChatHeader.jsx` (ou équivalent).

### 4.1. Contenu

Header en haut de la colonne centrale :

- À gauche : `Clara ● Prête` + modèle (`gpt-5.1`)
- Au centre (ou sous-titre) : status (ex : `En réflexion...`, `En attente`)
- À droite :
  - toggle `Debug ON / OFF`
  - bouton pour le **thème** (voir section 5).

### 4.2. Indicateur de réflexion

- Récupérer l’état “loading” / “isThinking” déjà utilisé pour spinner / trois points.
- Dans le header :
  - Quand Clara réfléchit : afficher un petit indicateur animé à côté de son nom, par ex : `●●●` avec animation CSS simple.
  - Quand inactif : juste `● Prête` en vert discret.

Dans la zone de chat, garder éventuellement les `...` classiques en bas pendant la génération.

---

## 5. Thèmes & couleurs (config centralisée)

Objectif : donner à l’utilisateur la possibilité de changer le look global **sans toucher au code** (ou avec un seul fichier).

### 5.1. Fichier de thème

Créer `src/config/theme.js` :

```js
export const themes = {
  // Thème clair futuriste (par défaut)
  light: {
    name: "Clair futuriste",
    background: "#f6f5f2",
    sidebarBg: "#f0eee8",
    sidebarBorder: "#dedad0",
    chatBg: "#ffffff",
    messageUserBg: "#2f3bff",
    messageUserText: "#ffffff",
    messageClaraBg: "#f2f0ea",
    messageClaraText: "#111111",
    accent: "#ffb200",
    textPrimary: "#111111",
    textSecondary: "#555555",
    borderSubtle: "#e0ddd5",
    inputBg: "#f5f3ee",
  },

  // Thème sombre actuel adapté
  dark: {
    name: "Sombre futuriste",
    background: "#020617",
    sidebarBg: "#020617",
    sidebarBorder: "#1e293b",
    chatBg: "#020617",
    messageUserBg: "#2563eb",
    messageUserText: "#ffffff",
    messageClaraBg: "#020617",
    messageClaraText: "#e5e7eb",
    accent: "#fbbf24",
    textPrimary: "#e5e7eb",
    textSecondary: "#9ca3af",
    borderSubtle: "#1e293b",
    inputBg: "#020617",
  },
};
```

Créer aussi un petit hook `useTheme` dans `src/styles/useTheme.js` qui :
- stocke le thème courant dans `localStorage`
- expose `theme` + `setTheme`

### 5.2. Application du thème

Dans `App.jsx` :

- Récupérer `theme` via `useTheme()`.
- Appliquer les couleurs via `style` ou via des classes CSS utilisant CSS variables :

Dans `main.jsx` : injecter les variables :

```jsx
useEffect(() => {
  const root = document.documentElement;
  Object.entries(theme).forEach(([key, value]) => {
    root.style.setProperty(`--${key}`, value);
  });
}, [theme]);
```

Puis dans le CSS (`src/styles/*.css`), utiliser :

```css
body {
  background: var(--background);
  color: var(--textPrimary);
}

.sidebar {
  background: var(--sidebarBg);
  border-right: 1px solid var(--sidebarBorder);
}

.message.user {
  background: var(--messageUserBg);
  color: var(--messageUserText);
}

.message.clara {
  background: var(--messageClaraBg);
  color: var(--messageClaraText);
}
```

### 5.3. Sélecteur de thème dans le header

Dans `ChatHeader.jsx` :

- Remplacer le simple bouton “soleil” par un bouton texte discret, ex : `Thème`.
- Au clic, ouvrir un petit menu (popover ou dropdown) avec :
  - `Clair futuriste`
  - `Sombre futuriste`
- Sur sélection : `setTheme('light')` ou `setTheme('dark')`.

Pas besoin de 10 thèmes pour l’instant : 2 bien propres suffisent, mais la structure permet d’en rajouter plus tard.

---

## 6. Nettoyage de l’ancienne sidebar droite

Supprimer / désactiver les blocs suivants :
- “Mémoire : Voir mes notes / todos / process / protocols / préférences / contacts”
- “Actions rapides : Reformuler / Résumer / Brainstorm”
- “Modes : Mode réflexion profonde / Sauvegarde auto notes / Utilisation auto mémoire”

Important :
- Ne pas supprimer la logique backend associée (auto-mémoire, etc.).  
- On enlève seulement les **boutons UI** pour l’instant.

Là où c’est pertinent, déplacer la logique vers :
- le `DetailsPanel` quand c’est vraiment du debug / interne,
- ou laisser le user passer par le langage naturel (“Montre-moi tous mes contacts”).

---

## 7. Style général (futuriste, simple, type Apple)

Dans les styles (`src/styles/*.css` ou équivalent) :

- Typo : si possible utiliser `system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif`.
- Coins légèrement arrondis (`border-radius: 12px` max sur les cards, 18px sur les bulles).
- Ombres très légères (`box-shadow: 0 10px 30px rgba(0,0,0,0.05)` pour les cards).
- Espacements généreux (`padding: 12px 16px` pour les bulles, `gap: 12px` entre messages).
- Pas d’animations lourdes. Juste :
  - `transition: background 0.2s, color 0.2s, box-shadow 0.2s;`
  - petite transition sur l’ouverture/fermeture du `DetailsPanel`.

---

## 8. À tester après implémentation

1. **Sessions**
   - Créer plusieurs sessions.
   - Renommer une session → le nouveau nom reste après refresh.
   - Supprimer une session → elle disparaît du côté UI et backend.
   - Supprimer toutes les sessions → la liste revient vide.

2. **Debug / Détails**
   - Debug OFF → aucun panneau “Détails” visible.
   - Debug ON → panneau “Détails” s’affiche sous les messages, repliable.
   - L’interaction avec le chat reste fluide même avec debug ON.

3. **Thèmes**
   - Changer de thème dans le header → toutes les couleurs principales se mettent à jour.
   - Fermer / rouvrir l’UI → le thème choisi est conservé (localStorage).

4. **Réactivité**
   - Interface utilisable sur fenêtre réduite (pas mobile complet, mais au moins 1024px de large).  
   - Aucun scroll horizontal parasite.

Comme d’habitude, documenter l’implémentation dans `journal/cursor_gpt/` avec un fichier du type :  
`2025-12-05_ui_v2_minimalist_implementation.md` (contexte, changements, limitations, TODO).
