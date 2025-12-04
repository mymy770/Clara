Corrige deux points importants dans l’orchestrator et les helpers mémoire.

1) Vérification mémoire obligatoire avant réponse
Actuellement, Clara peut dire qu’il n’y a “aucune note”, alors qu’il y en a dans la DB.
C’est parce que l’orchestrator s’appuie parfois uniquement sur le contexte du LLM.

➡️ Correction demandée :
- Pour chaque intention “list_*”, “search_*”, “get_*”, l’orchestrator doit obligatoirement appeler memory.search_memory_by_type() ou search_memory_by_keyword() AVANT de répondre.
- Aucune réponse ne doit être générée sans un passage explicite par la DB.

Objectif : garantir zéro hallucination pour les opérations de récupération.


2) Génération automatique de tags
Lors de l’enregistrement d’un élément (note, todo, process, protocole), si l’utilisateur ne donne pas de tags :
→ Clara doit générer automatiquement une liste de tags.
  - Extraire les mots clés importants du contenu (3 à 5 max)
  - Enlever les stopwords
  - Lowercase
  - Format liste JSON

Stocker ces tags dans le champ 'tags'.

Objectif : éviter tags=NULL dans la DB.


3) Documentation
Ajouter une note dans journal/cursor_gpt expliquant :
- pourquoi la vérification DB obligatoire est ajoutée
- pourquoi l’autotagging devient systématique
- comment c’était détecté dans les tests