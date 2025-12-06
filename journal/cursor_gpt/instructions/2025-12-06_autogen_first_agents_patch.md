# 2025-12-06 - Patch Autogen - Creation des premiers agents (FS, Memoire, Interprete)

Objectif :  
Mettre en place la premiere couche Autogen sans casser Clara actuelle :
- Garder `run_clara.py` et l'orchestrateur actuels INTACTS.
- Ajouter une nouvelle entree : `run_clara_autogen.py` pour tester le mode multi-agents.
- Creer 3 agents Autogen bases sur les fonctions qui marchent deja :
  - `InterpreterAgent` (cerveau / chef d'orchestre LLM)
  - `FSAgent` (file system, base sur `fs_driver.py`)
  - `MemoryAgent` (memoire, base sur `memory_core.py`)

L'idee : ne rien casser, juste ajouter une couche au-dessus.

---

## 1. Dependances Autogen

1. Ajoute dans `requirements.txt` (si ce n'est pas deja fait) :
   - `autogen`  (ou le package officiel que tu utilises deja, ajuste le nom si besoin)

2. Tu peux aussi isoler Autogen derriere un try/except pour eviter de planter si non installe,
   mais ce n'est pas obligatoire si on considere que l'env est maitrise.

---

## 2. Nouveau fichier - `agents/autogen_hub.py`

Cree un fichier : `agents/autogen_hub.py` avec la structure suivante :

```python
# agents/autogen_hub.py

"""
Hub Autogen pour Clara.
Definit les agents :
- InterpreterAgent : agent LLM principal qui parle a l'utilisateur et decide quoi faire
- FSAgent : agent specialise dans le filesystem, wrappe fs_driver
- MemoryAgent : agent specialise memoire, wrappe memory_core
"""

import os
from autogen import AssistantAgent, UserProxyAgent  # ou les classes equivalentes selon la version
from drivers.fs_driver import FSDriver
from memory.memory_core import MemoryCore

# 1. Recuperation config modele / cle dans settings.yaml + .env
#    -> utilise llm_driver ou une fonction utilitaire existante pour centraliser.
#    Objectif : eviter de dupliquer la config modele.

def build_llm_config():
    """Retourne un dict de config pour Autogen (model, api_key, base_url, etc.)"""
    # Idealement : reutiliser la config de llm_driver / settings.yaml
    ...

def create_fs_agent(llm_config: dict) -> AssistantAgent:
    """Agent specialise filesystem. N'a pas de conversation directe avec l'humain."""
    fs_driver = FSDriver(base_path=...)  # reutiliser la config FS existante

    def fs_tools():
        # Fonctions wrapper autour de FSDriver :
        # - create_dir
        # - create_file
        # - append_to_file
        # - read_file
        # - move_path
        # - delete_path
        # - list_dir
        ...
    # Creer un AssistantAgent avec un system_prompt clair + ces tools
    ...

def create_memory_agent(llm_config: dict) -> AssistantAgent:
    """Agent specialise memoire. Wrappe MemoryCore."""
    memory = MemoryCore(db_path=...)  # reutiliser la config actuelle

    def memory_tools():
        # Fonctions wrapper autour de MemoryCore :
        # - save_memory
        # - load_memory
        # - search_memory
        # - delete_memory
        # + helpers pour contacts / notes / todo / process / protocol / preferences
        ...
    # Creer un AssistantAgent avec un system_prompt clair + ces tools
    ...

def create_interpreter_agent(llm_config: dict,
                             fs_agent: AssistantAgent,
                             memory_agent: AssistantAgent) -> AssistantAgent:
    """Agent chef d'orchestre : parle a l'utilisateur et delegue."""
    # System prompt :
    # - Comprendre la demande utilisateur
    # - Decider quand appeler FSAgent
    # - Decider quand appeler MemoryAgent
    # - Repondre en texte clair
    ...
```

Important :  
- Pas de logique metier custom dans Autogen lui-meme.  
- Autogen doit appeler les outils qui appellent `FSDriver` et `MemoryCore`.  
- On ne reecrit pas la logique FS ou memoire, on la wrappe.

---

## 3. Nouveau fichier - `run_clara_autogen.py`

Cree un fichier a la racine du projet : `run_clara_autogen.py`

Role :  
- Point d'entree CLI pour tester le mode Autogen sans toucher au reste.
- Boucle simple : input() -> envoie a InterpreterAgent -> affiche la reponse.

Exemple de structure (pseudo-code) :

```python
# run_clara_autogen.py

"""
Entree simple en ligne de commande pour tester Clara Autogen (multi-agents).
Ne touche pas a l'UI ni a run_clara.py existant.
"""

from agents.autogen_hub import (
    build_llm_config,
    create_fs_agent,
    create_memory_agent,
    create_interpreter_agent,
)

def main():
    llm_config = build_llm_config()

    fs_agent = create_fs_agent(llm_config)
    memory_agent = create_memory_agent(llm_config)
    interpreter = create_interpreter_agent(llm_config, fs_agent, memory_agent)

    print("Clara Autogen - mode terminal. Tape 'quit' pour sortir.")

    while True:
        user_input = input("Vous: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break

        # Envoyer la requete a l'agent interprete
        # et afficher la reponse finale a l'utilisateur.
        response = ...  # Appel Autogen selon la version
        print(f"Clara: {response}")

if __name__ == "__main__":
    main()
```

Ne pas melanger ca avec l'UI pour l'instant.  
On veut un mode test simple en terminal pour valider les agents.

---

## 4. Integration avec la memoire et FS existants

But : utiliser ce qui marche deja tel quel.

1. FSAgent
   - Reutiliser `drivers/fs_driver.py` sans modification (sauf si bug existant).
   - Exposer les methodes suivantes comme tools Autogen :
     - `create_dir`
     - `create_file`
     - `append_to_file`
     - `read_file`
     - `move_path`
     - `delete_path`
     - `list_dir`
   - Le system prompt de FSAgent doit etre court et strict :
     - "Tu es un agent specialise filesystem.  
        Tu ne reponds jamais directement a l'utilisateur.  
        Tu executes uniquement les actions demandees via tes tools,  
        et tu retournes des resultats structures (succes/echec + details)."

2. MemoryAgent
   - Reutiliser `memory/memory_core.py` et son API actuelle :
     - `save_memory(category, content, tags=None, metadata=None, ...)`
     - `search_memory(...)`
     - `load_memory(...)`
     - `delete_memory(...)`
   - Fournir des helpers/tools pour :
     - `save_note`, `list_notes`
     - `save_todo`, `list_todos`, `complete_todo`
     - `save_process`, `list_processes`
     - `save_protocol`, `list_protocols`
     - `save_preference`, `list_preferences`
     - `save_contact`, `get_contact`, `update_contact`
   - System prompt de MemoryAgent :
     - Agent specialise memoire, jamais de reponse utilisateur directe,  
       uniquement des operations CRUD sur la base memoire.

3. InterpreterAgent
   - Role :  
     - Comprendre la demande utilisateur.  
     - Decider si :
       - just answer (explication / reformulation)  
       - demander quelque chose au MemoryAgent  
       - demander quelque chose au FSAgent  
     - Composer la reponse finale.

   - System prompt :
     - "Tu es Clara, agent principal.  
        Tu peux appeler d'autres agents (FS, Memory) quand c'est utile.  
        Tu dois toujours donner une reponse claire a l'utilisateur a la fin.  
        Tu ne touches jamais directement au filesystem ni a la base de donnees :  
        tu passes par FSAgent et MemoryAgent."

---

## 5. Journalisation / Logs Autogen

Sans aller trop loin pour l'instant, ajoute un log minimal pour le mode Autogen :

- Nouveau fichier log : `logs/sessions/autogen_session_<timestamp>.jsonl`
- Pour chaque tour :
  - entree user
  - agent(s) appeles
  - tools appeles (FS / Memory)
  - erreur eventuelle
  - reponse finale

Pas besoin d'un truc parfait maintenant, juste suffisamment lisible pour debugger.

---

## 6. Discipline Git / Journaux

1. Ajoute une entree dans `journal/cursor_gpt/` :
   - `2025-12-06_autogen_first_agents.md`
   - Contenu : resume des fichiers crees, des decisions d'architecture, et des limites.

2. Commit recommande :
   - `feat: add first Autogen agents (FS, Memory, Interpreter)`

---

## 7. Rappels importants

- Ne touche pas a :
  - `run_clara.py`
  - Orchestrator actuel
  - UI actuelle

- Ce patch est 100% additif :
  - On ajoute Autogen a cote.
  - On testera Clara en mode Autogen via `python run_clara_autogen.py`.

- Si certaines fonctions existent deja (helpers, wrappers, etc.) :
  - Reutilise-les au lieu de dupliquer.
  - Si un nom de fichier differe legerement, adapte en consequence,
    mais garde la meme philosophie : agents specialises, orchestrateur separe.
