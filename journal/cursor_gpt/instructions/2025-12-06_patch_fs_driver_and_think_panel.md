# 2025-12-06 – Patch FS Driver + THINK / PLAN / SYNC Panel (UI Clara)

## 🎯 Objectif
1. Corriger le FS-Driver qui n’exécute pas réellement les opérations (write/read).
2. Faire en sorte que Clara **affiche la réponse du FS Driver** (ex: contenu d’un fichier lu) au lieu de juste afficher le JSON d’intention.
3. Rétablir un panneau THINK/PLAN/SYNC fonctionnel :
   - THINK = raisonnement interne
   - PLAN  = to-do interne (arbre d’action)
   - SYNC  = opérations mémoire / FS réellement exécutées
4. Faire en sorte que **Cursor teste Clara en vrai** avant de pousser une modification.

---

# 1. Correctifs pour `fs_driver.py`

## 🔧 Problème
Ton test UI montre :
- Clara génère bien l’intention JSON.
- MAIS le driver ne renvoie rien dans l’interface → l’UI ne reçoit aucune sortie utile.

## ✅ Action demandée à Cursor
Corriger :  
- write_text  
- read_text  
- list_dir  
- delete_file  
pour qu’ils **retournent un dictionnaire exploitable par l’UI**.

### ✔ Code attendu (à implémenter dans `drivers/fs_driver.py`) :

```python
def write_text(path: str, content: str):
    full_path = BASE_PATH / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return {
        "status": "success",
        "message": f"File written: {path}"
    }

def read_text(path: str):
    full_path = BASE_PATH / path
    if not full_path.exists():
        return {"status": "error", "message": "File does not exist."}
    return {
        "status": "success",
        "content": full_path.read_text(encoding="utf-8")
    }
2. Correctif orchestrator : exécuter le driver puis retourner un VRAI message

🔧 Problème

L’orchestrateur renvoie uniquement l’intention JSON → pas l’exécution réelle.

✅ Action demandée

Modifier la partie :
if intent["intent"] == "filesystem":
    result = fs_driver.run(intent)
    return format_to_ui(result)
result doit contenir les données du driver (contenu d’un fichier, confirmation écriture, etc.).

⸻

3. Mise en place du vrai panneau THINK / PLAN / SYNC

🎨 Interfaces demandées

👉 THINK
	•	Affiche les thoughts bruts envoyés par Clara.
	•	Format scrollable.
	•	Onglet dédié.

👉 PLAN
	•	Affiche la todo interne générée par Clara :
	•	liste d’étapes
	•	étapes effectuées → barrées automatiquement

👉 SYNC
	•	Liste de toutes les opérations effectuées :
	•	actions mémoire
	•	actions FS
	•	modifications de contacts, préférences, etc.

✔ Code attendu UI (components/ThinkPanel.jsx, etc.)

Cursor doit :
	•	Réactiver l’écoute des clés JSON think, plan, sync dans le websocket.
	•	Afficher proprement ces blocs dans 3 onglets distincts.

⸻

4. Obligation de test par Cursor (IMPORTANT)

Ajouter dans TOUT patch :
Avant de considérer la tâche comme terminée,
ouvre un terminal, lance Clara avec :

1) uvicorn api_server:app --reload --port 8001
2) cd ui/chat_frontend && npm run dev

Puis teste les 4 commandes suivantes :
- "Crée un fichier test_fs/demo.txt avec le contenu : Bonjour Clara."
- "Lis le fichier test_fs/demo.txt."
- "Supprime test_fs/demo.txt."
- "Montre-moi mon plan / sync / réflexion."

Si l’interface n’affiche pas correctement :
- le contenu du fichier lu
- les logs dans THINK / PLAN / SYNC

Alors le patch doit être corrigé AVANT livraison.
5. Résultat attendu FINAL

Après ce patch, Clara doit :

✔ Créer un fichier réel → visible dans le dossier

✔ Lire le fichier → afficher le contenu dans le chat

✔ Montrer dans SYNC :
FS write : test_fs/demo.txt
FS read : test_fs/demo.txt
✔ Montrer dans PLAN :
1. Vérifier le chemin
2. Écrire le fichier
3. Confirmer l’opération
✔ Montrer dans THINK :

Les étapes internes de réflexion.

⸻

6. À appliquer dans Cursor

Dans un message à Cursor :
Voici un patch complet à appliquer :

1. Corriger fs_driver.py pour renvoyer un résultat exploitable.
2. Modifier orchestrator.py pour exécuter réellement le driver et renvoyer sa sortie.
3. Mettre à jour l’UI pour afficher THINK / PLAN / SYNC en trois panneaux fonctionnels.
4. Tester Clara en vrai (uvicorn + npm run dev) avant de livrer.

Tu DOIS valider en lançant Clara et en testant 4 commandes FS.
Voici un patch complet à appliquer :

1. Corriger fs_driver.py pour renvoyer un résultat exploitable.
2. Modifier orchestrator.py pour exécuter réellement le driver et renvoyer sa sortie.
3. Mettre à jour l’UI pour afficher THINK / PLAN / SYNC en trois panneaux fonctionnels.
4. Tester Clara en vrai (uvicorn + npm run dev) avant de livrer.

Tu DOIS valider en lançant Clara et en testant 4 commandes FS.
Fin du patch.
