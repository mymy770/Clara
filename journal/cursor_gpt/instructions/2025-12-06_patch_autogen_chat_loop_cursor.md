# 2025-12-06_patch_autogen_chat_loop_cursor.md

## 🎯 Contexte (pour Cursor)
Projet : **Clara**  
Objectif : corriger le nouveau mode **Autogen** qui :
- continue à parler même quand l’utilisateur n’envoie plus rien,
- adopte un ton « thérapeute » au lieu d’un agent technique,
- boucle 5 fois tout seul puis termine sur `Maximum turns reached`,
- affiche des warnings de modèle non trouvé.

Ce patch doit :  
1. Rendre la boucle de chat **100% pilotée par l’entrée utilisateur**.  
2. Rendre l’agent `interpreter` **sec, technique, non-psychologique**.  
3. Nettoyer les warnings Autogen sur le modèle.  
4. Tester en **conditions réelles** dans le terminal avant de considérer la tâche comme terminée.

---

## ✅ 1. Fixer la boucle de chat dans `run_clara_autogen.py`

### 1.1. Ouvrir le fichier
- Fichier : `run_clara_autogen.py` à la racine du projet Clara.

### 1.2. Remplacer la boucle de chat par une version contrôlée
**But :** ne jamais envoyer de message vide au modèle, gérer `quit/exit`, et limiter explicitement les tours.

1. Localise la boucle principale qui lit l’entrée utilisateur (celle qui affiche `Clara Autogen - Mode terminal` et demande `Vous:`).
2. Remplace **toute** la boucle `while True:` par ceci :

```python
while True:
    user_input = input("\nVous: ").strip()

    # 1 — Quitter proprement
    if user_input.lower() in {"quit", "exit"}:
        print("🔚 Fermeture de Clara Autogen.")
        break

    # 2 — Entrée vide → on n’envoie rien au modèle
    if user_input == "":
        print("(aucune entrée détectée)")
        continue

    # 3 — Envoyer au user_proxy / interpreter avec un nombre de tours limité
    try:
        response = user_proxy.initiate_chat(
            interpreter,
            message=user_input,
            max_turns=3
        )
        # Autogen renvoie un objet, on affiche soit un résumé, soit le dernier message
        if hasattr(response, "summary") and response.summary:
            print("\nClara:", response.summary)
        elif hasattr(response, "chat_history") and response.chat_history:
            last = response.chat_history[-1]
            content = last.get("content") if isinstance(last, dict) else str(last)
            print("\nClara:", content)
        else:
            print("\nClara: (pas de réponse)")
    except Exception as e:
        print(f"❌ Erreur Autogen: {e}")
```

**Contraintes :**
- Ne garde **aucun** appel à `initiate_chat` qui n’utilise pas `user_input`.
- Ne laisse **aucune** boucle qui déclenche une nouvelle requête si l’utilisateur n’a rien tapé.
- `max_turns` doit être petit (2–3), pas 5+.

---

## ✅ 2. Rendre l’agent `interpreter` technique (plus de psy)

### 2.1. Localiser la création de l’agent
Dans `run_clara_autogen.py`, tu dois avoir une création d’agent du type :

```python
interpreter = ConversableAgent(
    name="interpreter",
    system_message=...,
    ...
)
```

### 2.2. Remplacer le `system_message`

Remplace le contenu actuel de `system_message` par :

```python
system_message = """
Tu es Clara, un agent technique et logique.
Tu réponds court, net, analytique, sans blabla émotionnel.

Règles strictes :
- Tu n’es PAS un thérapeute.
- Tu ne supposes PAS que l’utilisateur est bloqué, triste ou anxieux.
- Tu ne proposes PAS de menus d’options type 1/2/3 "si tu ne sais pas quoi dire".
- Tu ne continues PAS la conversation tout seul.
- Tu ne relances PAS si l’utilisateur n’envoie rien.

Ton rôle :
- Comprendre l’instruction utilisateur.
- Répondre de façon précise, technique et utile.
- Quand on te parle de fichiers, mémoire, agents, projet Clara, tu te comportes comme un assistant dev/ops.

Si l’utilisateur n’envoie rien → tu ne dois rien produire.
"""
```

Assure-toi que `system_message` est bien passé à l’agent `interpreter`.

---

## ✅ 3. Nettoyer les warnings Autogen « Model not found »

### 3.1. Ouvrir `autogen_hub.py`
- Fichier : `autogen_hub.py` (ou équivalent) là où est définie la `config_list` pour les modèles.

### 3.2. Ajouter un prix par défaut pour le modèle `gpt-5.1-2025-11-13`

Dans la config du modèle OpenAI que tu utilises (`gpt-5.1-2025-11-13`), ajoute un champ `price` pour éviter le warning :

Exemple :

```python
config_list = [
    {
        "model": "gpt-5.1-2025-11-13",
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "price": [0.000002, 0.000006],  # prompt / completion par 1k tokens (valeur arbitraire)
    },
]
```

Si la config est structurée différemment, adapte mais garde l’idée :
- même modèle,
- ajout du champ `price` avec un tableau `[prompt_price, completion_price]`.

---

## ✅ 4. Désactiver comportements implicites Autogen (optionnel mais recommandé)

Toujours dans `run_clara_autogen.py`, **avant** la création des agents, ajoute :

```python
from autogen import settings

settings.disable_telemetry = True
settings.allow_non_api_models = True
```

Ça ne change pas la logique métier, mais évite certains comportements implicites et warnings Autogen.

---

## ✅ 5. Tests obligatoires (EN LOCAL avant de dire “terminé”)

Après les modifications, **TU DOIS** tester en réel :

1. Dans le dossier `Clara` :  
   ```bash
   python3 run_clara_autogen.py
   ```

2. Vérifier la séquence suivante :  
   - L’app affiche bien le header `Clara Autogen - Mode terminal`.
   - Tu tapes : `salut` → Clara répond **une seule fois** avec une réponse courte, technique (pas psy).
   - Tu appuies juste sur Entrée (ligne vide) → le terminal affiche `(aucune entrée détectée)` et **Clara ne répond PAS**.
   - Tu tapes une deuxième question réelle → Clara répond normalement.
   - Tu tapes `quit` ou `exit` → le programme sort proprement sans stacktrace.

3. Si l’un de ces points échoue → corrige et relance les tests avant de considérer la mission terminée.

---

## 🧾 Journalisation (journal/cursor_gpt)

À la fin :  
- Crée ou mets à jour un fichier dans `journal/cursor_gpt/` avec un nom du type :  
  `2025-12-06_autogen_chat_loop_fix.md`

Contenu minimum :
- Contexte du bug (boucle, ton thérapeute, warnings).
- Fichiers modifiés (`run_clara_autogen.py`, `autogen_hub.py`).
- Rappel des tests effectués et résultat.
- TODO éventuels pour la suite (ex : future intégration d’autres agents).

---

## ✅ Résultat attendu

Après ce patch, en situation réelle :
- Clara Autogen ne parle **que** quand l’utilisateur envoie quelque chose.
- Pas de relance automatique, pas de menus 1/2/3, pas de “je vois que tu n’écris rien”.
- Le ton est **technique, sec, utile**, adapté au projet Clara.
- Plus de warning Autogen sur le modèle.
- La boucle terminal est **prévisible, maîtrisée**.
