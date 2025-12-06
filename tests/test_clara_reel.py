#!/usr/bin/env python3
"""
Tests en conditions réelles avec Clara
Teste les actions via l'orchestrateur complet
"""

import sys
import json
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestrator import Orchestrator
from memory.memory_core import init_db, get_items
from memory.helpers import save_note, save_todo
from utils.logger import DebugLogger
from datetime import datetime

def test_clara_delete_all_notes():
    """Test réel : Clara supprime toutes les notes"""
    print("\n=== TEST RÉEL : Clara supprime toutes les notes ===")
    
    init_db()
    orchestrator = Orchestrator()
    session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    debug_logger = DebugLogger(session_id)
    
    # Créer quelques notes d'abord
    id1 = save_note("Note test Clara 1")
    id2 = save_note("Note test Clara 2")
    print(f"✓ Notes créées: {id1}, {id2}")
    
    # Vérifier qu'elles existent
    notes_before = get_items(type='note')
    print(f"✓ Notes avant: {len(notes_before)}")
    
    # Demander à Clara de supprimer toutes les notes
    response = orchestrator.handle_message("suprimes toutes les notes", session_id, debug_logger)
    print(f"✓ Réponse Clara: {response.get('response', 'N/A')[:100]}")
    
    # Vérifier qu'elles sont supprimées
    notes_after = get_items(type='note')
    print(f"✓ Notes après: {len(notes_after)}")
    
    if len(notes_after) == 0:
        print("✅ SUCCÈS : Toutes les notes supprimées")
        return True
    else:
        print(f"❌ ÉCHEC : {len(notes_after)} notes restantes")
        return False

def test_clara_delete_all_todos():
    """Test réel : Clara supprime tous les todos"""
    print("\n=== TEST RÉEL : Clara supprime tous les todos ===")
    
    init_db()
    orchestrator = Orchestrator()
    session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    debug_logger = DebugLogger(session_id)
    
    # Créer quelques todos d'abord
    id1 = save_todo("Todo test Clara 1")
    id2 = save_todo("Todo test Clara 2")
    print(f"✓ Todos créés: {id1}, {id2}")
    
    # Vérifier qu'ils existent
    todos_before = get_items(type='todo')
    print(f"✓ Todos avant: {len(todos_before)}")
    
    # Demander à Clara de supprimer tous les todos
    response = orchestrator.handle_message("suprimes tous les todos", session_id, debug_logger)
    print(f"✓ Réponse Clara: {response.get('response', 'N/A')[:100]}")
    
    # Vérifier qu'ils sont supprimés
    todos_after = get_items(type='todo')
    print(f"✓ Todos après: {len(todos_after)}")
    
    if len(todos_after) == 0:
        print("✅ SUCCÈS : Tous les todos supprimés")
        return True
    else:
        print(f"❌ ÉCHEC : {len(todos_after)} todos restants")
        return False

def test_all_clara_real():
    """Tests complets en conditions réelles"""
    print("\n" + "="*60)
    print("TESTS EN CONDITIONS RÉELLES AVEC CLARA")
    print("="*60)
    
    results = []
    
    try:
        results.append(("Clara delete_all_notes", test_clara_delete_all_notes()))
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Clara delete_all_notes", False))
    
    try:
        results.append(("Clara delete_all_todos", test_clara_delete_all_todos()))
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Clara delete_all_todos", False))
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS RÉELS")
    print("="*60)
    for name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "="*60)
    if all_passed:
        print("✅ TOUS LES TESTS RÉELS SONT PASSÉS")
    else:
        print("❌ CERTAINS TESTS RÉELS ONT ÉCHOUÉ")
    print("="*60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = test_all_clara_real()
    sys.exit(0 if success else 1)

