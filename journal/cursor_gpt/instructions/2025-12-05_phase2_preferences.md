# ============================
#  PATCH CURSOR – PHASE 2 : PREFERENCES
#  Projet : Clara
#  Date : 2025-12-05
# ============================
# OBJECTIF :
# Implémenter totalement le système de "préférences" dans la mémoire Clara :
# - Modèle stable, propre, cohérent
# - Stockage en SQLite (memory.sqlite)
# - Helpers dans memory_core.py
# - Détection simple dans l'orchestrator
# - Aucun impact sur contacts / notes / todos
# 
# IMPORTANT : Ne rien modifier en dehors de ce qui est listé.
# Aucun agent, aucun driver, aucune logique phase 3/4/5.
# ============================


# =========================================================
# 1. AJOUTER LE TYPE "preference" DANS memory_core.py
# =========================================================

# Dans memory_core.py :
# Ajouter un nouveau type dans les opérations génériques existantes.
# Le modèle d'une préférence suit cette structure :

# {
#   "scope": "global" | "agent",
#   "agent": "mail" | "calendar" | "orchestrator" | null,
#   "domain": "communication" | "ui" | "agenda" | ...,
#   "key": "preferred_channel",
#   "value": "whatsapp",
#   "source": "user" | "inferred",
#   "confidence": float (0.0–1.0)
# }

# Ajouter les fonctions suivantes :

def save_preference(pref: dict) -> bool:
    """Insère ou met à jour une préférence selon key+scope+agent."""
    # - Vérifier si une préférence similaire existe déjà
    # - Si oui → UPDATE
    # - Si non → INSERT
    # Retourne True/False

def get_preference_by_key(key: str):
    """Retourne la préférence correspondant à key."""

def list_preferences():
    """Liste toutes les préférences stockées."""

def search_preferences(query: str):
    """Recherche textuelle dans key/value/domain."""

# Utiliser exactement la même philosophie et structure que :
# save_note(), save_contact(), save_process(), save_protocol()


# =========================================================
# 2. MODIFICATION DU SCHEMA SQL : schema.sql
# =========================================================
# Ajouter une table dédiée :

CREATE TABLE IF NOT EXISTS preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scope TEXT,
    agent TEXT,
    domain TEXT,
    key TEXT UNIQUE,
    value TEXT,
    source TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# IMPORTANT :
# - Ne toucher à aucune autre table existante
# - Ne pas renommer
# - Ne pas modifier la structure actuelle


# =========================================================
# 3. ORCHESTRATOR : DÉTECTION DES PRÉFÉRENCES
# =========================================================
# Dans orchestrator.py, dans la zone d'analyse des intentions,
# ajouter un détecteur simple :

# Si une phrase correspond à :
#   - "je préfère ..."
#   - "désormais ..."
#   - "à partir de maintenant ..."
#   - "toujours ..."
#   - "ne jamais ..."
# Alors intention = "set_preference"

# Exemple :
# "À partir de maintenant, parle toujours en français"
# doit donner :
# {
#   "intent": "set_preference",
#   "key": "language",
#   "value": "fr",
#   "scope": "global",
#   "agent": "orchestrator"
# }

# Clara NE DOIT PAS demander confirmation
# sauf s'il existe ambiguité (plusieurs agents possibles).


# =========================================================
# 4. EXECUTION DE L'INTENTION DANS orchestrator.py
# =========================================================

if intent == "set_preference":
    result = memory.save_preference(parsed_pref_dict)
    return {
        "response": f"Préférence enregistrée : {parsed_pref_dict['key']} = {parsed_pref_dict['value']}",
        "status": "ok"
    }


# =========================================================
# 5. TAG AUTOMATIQUE
# =========================================================
# Après save_preference(), appeler save_memory() avec :
# tags=["preference", parsed_pref_dict["domain"], parsed_pref_dict["agent"] or "global"]

# Les tags doivent être cohérents et propres.


# =========================================================
# 6. TESTS (à ajouter dans tests/test_memory_core.py)
# =========================================================

def test_preference_write_read():
    # Créer une préférence
    # Lire la préférence
    # Vérifier que key, value, scope, domain, agent sont corrects
    assert True

# Tests simples uniquement, pas de test orchestrator.


# =========================================================
# 7. JOURNALISATION
# =========================================================
# Créer un fichier :
# journal/cursor_gpt/2025-12-05_phase2_preferences.md
#
# Contenu :
# - Résumé des fichiers modifiés
# - Décisions techniques appliquées
# - Instructions non traitées
# - Prochaines étapes


# =========================================================
# FIN DU PATCH
# =========================================================