# 2025-12-06 – Patch UI : Réflexion / Plan d’action / Process internes

Objectif :  
Reconnecter l’UI aux infos internes de Clara (réflexion, plan d’action, étapes exécutées) **sans toucher au backend**, en utilisant ce qui est déjà renvoyé par l’API (JSON de l’orchestrator).  
On veut :
- un panneau à droite repliable « Détails internes »
- 3 sous-sections : **Réflexion**, **Plan d’action**, **Étapes exécutées**
- pas de spam : affichage court, utile, lisible

---

## 1. Points de départ (à vérifier dans le code actuel)

Dans `ui/chat_frontend/src/api.js` (ou équivalent), tu as déjà quelque chose comme :

- un appel POST vers notre backend (`/chat` ou similaire)
- une réponse JSON qui contient au minimum :
  - `answer` (texte final pour l’utilisateur)
  - et un objet / champ utilisé pour le debug interne (ex : `debug`, `meta`, `internal`…)

➡️ Inspecte **la réponse réelle** renvoyée par l’API (via console log) pour confirmer les champs exacts qui existent déjà, par exemple :

```js
console.log("Clara raw response", data);
```

L’idée est de brancher l’UI **sur les champs qui existent déjà**, par exemple (à adapter à la réalité) :

- `data.debug.thoughts`       → Réflexion
- `data.debug.todo_plan`      → Plan d’action
- `data.debug.memory_ops`     → Étapes exécutées

Si les noms sont différents, adapte les sélecteurs, mais **ne rajoute aucun champ côté backend**.

---

## 2. État React : où stocker ces infos

Dans `ui/chat_frontend/src/App.jsx` (ou composant principal du chat) :

1. Ajoute de l’état pour les vues internes :

```jsx
const [internalThoughts, setInternalThoughts] = useState(null);
const [internalTodo, setInternalTodo] = useState(null);
const [internalSteps, setInternalSteps] = useState(null);
const [showInternalPanel, setShowInternalPanel] = useState(true); // panneau repliable
```

2. Quand tu reçois la réponse de Clara (là où tu ajoutes le message de Clara à la conversation), récupère aussi les champs internes :

Exemple (à adapter) :

```jsx
// Après avoir reçu `data` depuis l’API Clara
setMessages(prev => [...prev, {
  role: "assistant",
  content: data.answer || "(Réponse vide)"
}]);

// Récupération défensive des champs internes
const dbg = data.debug || data.meta || {};

setInternalThoughts(
  dbg.thoughts || dbg.internal_thoughts || null
);

setInternalTodo(
  dbg.todo_plan || dbg.plan || null
);

setInternalSteps(
  dbg.memory_ops || dbg.steps || dbg.operations || null
);
```

⚠️ Important :  
- Ne jette rien, ne transforme pas le JSON backend.  
- Si un champ n’existe pas, tu le laisses à `null` → l’UI affichera « rien pour le moment ».  

---

## 3. Nouveau panneau « Détails internes » (droite)

Dans `ui/chat_frontend/src/components` :

1. Crée un composant `InternalPanel.jsx` :

```jsx
// ui/chat_frontend/src/components/InternalPanel.jsx
import React from "react";

export function InternalPanel({
  thoughts,
  todo,
  steps,
  open,
  onToggle,
}) {
  if (!open) {
    return (
      <div className="internal-panel internal-panel--collapsed">
        <button onClick={onToggle} className="internal-toggle">
          ▶ Détails internes
        </button>
      </div>
    );
  }

  return (
    <div className="internal-panel">
      <div className="internal-header">
        <span>Détails internes</span>
        <button onClick={onToggle} className="internal-toggle">
          ✕
        </button>
      </div>

      <div className="internal-section">
        <h4>🧠 Réflexion</h4>
        {renderThoughts(thoughts)}
      </div>

      <div className="internal-section">
        <h4>✅ Plan d’action</h4>
        {renderTodo(todo)}
      </div>

      <div className="internal-section">
        <h4>⚙️ Étapes exécutées</h4>
        {renderSteps(steps)}
      </div>
    </div>
  );
}

function renderThoughts(thoughts) {
  if (!thoughts) return <p className="internal-empty">Aucune réflexion disponible.</p>;

  if (typeof thoughts === "string") {
    const trimmed = thoughts.split("\n").slice(0, 4).join("\n");
    return <pre className="internal-block">{trimmed}</pre>;
  }

  // Si c’est un tableau de phrases
  if (Array.isArray(thoughts)) {
    return (
      <ul className="internal-list">
        {thoughts.slice(0, 4).map((t, i) => (
          <li key={i}>{t}</li>
        ))}
      </ul>
    );
  }

  return <pre className="internal-block">{JSON.stringify(thoughts, null, 2)}</pre>;
}

function renderTodo(todo) {
  if (!todo) return <p className="internal-empty">Aucun plan d’action pour le moment.</p>;

  // Autoriser string OU liste d’étapes
  if (typeof todo === "string") {
    // Si Clara renvoie une liste numérotée en texte
    return (
      <pre className="internal-block">
        {todo.split("\n").slice(0, 10).join("\n")}
      </pre>
    );
  }

  if (Array.isArray(todo)) {
    return (
      <ol className="internal-list">
        {todo.slice(0, 10).map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ol>
    );
  }

  return <pre className="internal-block">{JSON.stringify(todo, null, 2)}</pre>;
}

function renderSteps(steps) {
  if (!steps) return <p className="internal-empty">Aucune étape exécutée pour le moment.</p>;

  if (typeof steps === "string") {
    return (
      <pre className="internal-block">
        {steps.split("\n").slice(0, 10).join("\n")}
      </pre>
    );
  }

  if (Array.isArray(steps)) {
    return (
      <ul className="internal-list">
        {steps.slice(0, 10).map((s, i) => (
          <li key={i}>{s}</li>
        ))}
      </ul>
    );
  }

  return <pre className="internal-block">{JSON.stringify(steps, null, 2)}</pre>;
}
```

2. Dans `App.jsx`, intègre ce composant dans le layout à droite :

```jsx
import { InternalPanel } from "./components/InternalPanel";

// …dans le JSX principal…
<InternalPanel
  thoughts={internalThoughts}
  todo={internalTodo}
  steps={internalSteps}
  open={showInternalPanel}
  onToggle={() => setShowInternalPanel(prev => !prev)}
/>
```

3. Style minimal (dans `styles/internal.css` ou équivalent, et import dans `main.jsx` ou `App.jsx`) :

```css
.internal-panel {
  display: flex;
  flex-direction: column;
  width: 280px;
  border-left: 1px solid #e5e5e5;
  padding: 8px;
  background: #fafafa;
  font-size: 12px;
}

.internal-panel--collapsed {
  display: flex;
  justify-content: flex-end;
  padding: 4px;
}

.internal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 600;
}

.internal-section {
  margin-bottom: 8px;
}

.internal-block {
  background: #f3f3f3;
  border-radius: 4px;
  padding: 6px;
  white-space: pre-wrap;
}

.internal-list {
  margin: 4px 0;
  padding-left: 16px;
}

.internal-empty {
  color: #999;
  font-style: italic;
}

.internal-toggle {
  border: none;
  background: none;
  cursor: pointer;
  font-size: 11px;
  color: #555;
}
```

Tu peux ajuster les couleurs pour coller au thème actuel (clair / sombre), mais garde ça **sobre** et lisible.

---

## 4. Nettoyage : boutons et panneaux inutiles

1. **Supprimer les boutons “Voir mes notes / todos / process / contacts”** si ils ne sont que des raccourcis de prompt.
   - Soit tu les retires de l’UI,
   - Soit tu les caches derrière un simple menu secondaire, mais **par défaut**, l’écran doit rester minimal.

2. **Actions rapides (reformuler, résumer, brainstorm)** :  
   - Option : garder 2–3 boutons max, alignés sous la zone de saisie, ou dans un petit menu.  
   - Si ça surcharge, on les retire pour l’instant.

3. **Switchs “Mode réflexion profonde / Sauvegarde auto notes / Utilisation auto mémoire”** :  
   - Pour l’instant : soit tu les retires complètement,
   - soit tu les laisses visibles mais désactivés (`disabled`) avec un petit label “bientôt” — mais ils ne doivent pas donner l’impression d’être fonctionnels.

---

## 5. Vérifications à faire après patch

1. Lancer le frontend comme d’habitude, envoyer une requête un peu complexe (plusieurs étapes).
2. Ouvrir la console (Chrome DevTools) et vérifier :
   - la réponse JSON contient bien un objet debug/meta,
   - les champs utilisés dans `setInternalThoughts / setInternalTodo / setInternalSteps` existent ou sont `undefined` sans erreur.
3. Vérifier visuellement :
   - le panneau “Détails internes” apparaît bien à droite,
   - il est repliable / dépliable,
   - la réflexion reste courte (max ~4 lignes),
   - le plan d’action ressemble à une TODO liste,
   - les étapes exécutées sont lisibles sans scroller 3 km.

Si un des champs internes n’est **jamais** rempli, ce n’est pas un bug UI mais un sujet backend (orchestrator) à voir séparément.
