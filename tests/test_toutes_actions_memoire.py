#!/usr/bin/env python3
"""
Tests complets de toutes les actions mémoire en conditions réelles
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestrator import Orchestrator
from memory.memory_core import init_db, get_items
from memory.helpers import save_note, save_todo, save_process, save_protocol
from utils.logger import DebugLogger
from datetime import datetime

def test_action(action_name, user_message, create_items_func, get_items_func, verify_func):
    """Test générique d'une action"""
    print(f"\n=== TEST : {action_name} ===")
    
    init_db()
    orchestrator = Orchestrator()
    session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    debug_logger = DebugLogger(session_id)
    
    # Créer des items de test
    items_before = create_items_func()
    print(f"✓ Items créés: {len(items_before)}")
    
    # Vérifier l'état initial
    initial_count = len(get_items_func())
    print(f"✓ État initial: {initial_count} items")
    
    # Exécuter l'action via Clara
    response = orchestrator.handle_message(user_message, session_id, debug_logger)
    response_text = response.get('response', '')
    print(f"✓ Réponse Clara: {response_text[:80]}...")
    
    # Vérifier le résultat
    final_count = len(get_items_func())
    print(f"✓ État final: {final_count} items")
    
    # Vérification
    success = verify_func(initial_count, final_count, response_text)
    if success:
        print(f"✅ {action_name} : RÉUSSI")
    else:
        print(f"❌ {action_name} : ÉCHEC")
    
    return success

def test_save_note():
    """Test save_note"""
    def create():
        return [save_note("Note test save")]
    def get():
        return get_items(type='note')
    def verify(before, after, response):
        return after > before and "sauvegardée" in response.lower()
    return test_action("save_note", "enregistre une note : test save", create, get, verify)

def test_list_notes():
    """Test list_notes"""
    def create():
        return [save_note("Note test list 1"), save_note("Note test list 2")]
    def get():
        return get_items(type='note')
    def verify(before, after, response):
        return "note" in response.lower() and (str(before) in response or "trouvée" in response.lower())
    return test_action("list_notes", "liste toutes les notes", create, get, verify)

def test_save_todo():
    """Test save_todo"""
    def create():
        return [save_todo("Todo test save")]
    def get():
        return get_items(type='todo')
    def verify(before, after, response):
        return after > before and "sauvegardé" in response.lower()
    return test_action("save_todo", "enregistre un todo : test save", create, get, verify)

def test_list_todos():
    """Test list_todos"""
    def create():
        return [save_todo("Todo test list 1"), save_todo("Todo test list 2")]
    def get():
        return get_items(type='todo')
    def verify(before, after, response):
        return "todo" in response.lower() and (str(before) in response or "trouvé" in response.lower())
    return test_action("list_todos", "liste tous les todos", create, get, verify)

def test_delete_all_notes():
    """Test delete_all_notes"""
    def create():
        return [save_note("Note test delete 1"), save_note("Note test delete 2")]
    def get():
        return get_items(type='note')
    def verify(before, after, response):
        return after == 0 and "supprimée" in response.lower()
    return test_action("delete_all_notes", "suprimes toutes les notes", create, get, verify)

def test_delete_all_todos():
    """Test delete_all_todos"""
    def create():
        return [save_todo("Todo test delete 1"), save_todo("Todo test delete 2")]
    def get():
        return get_items(type='todo')
    def verify(before, after, response):
        return after == 0 and "supprimé" in response.lower()
    return test_action("delete_all_todos", "suprimes tous les todos", create, get, verify)

def test_save_process():
    """Test save_process"""
    def create():
        return [save_process("Process test save")]
    def get():
        return get_items(type='process')
    def verify(before, after, response):
        return after > before and "sauvegardé" in response.lower()
    return test_action("save_process", "enregistre un processus : test save", create, get, verify)

def test_list_processes():
    """Test list_processes"""
    def create():
        return [save_process("Process test list 1"), save_process("Process test list 2")]
    def get():
        return get_items(type='process')
    def verify(before, after, response):
        return "processus" in response.lower() and (str(before) in response or "trouvé" in response.lower())
    return test_action("list_processes", "liste tous les processus", create, get, verify)

def test_save_protocol():
    """Test save_protocol"""
    def create():
        return [save_protocol("Protocol test save")]
    def get():
        return get_items(type='protocol')
    def verify(before, after, response):
        return after > before and "sauvegardé" in response.lower()
    return test_action("save_protocol", "enregistre un protocole : test save", create, get, verify)

def test_list_protocols():
    """Test list_protocols"""
    def create():
        return [save_protocol("Protocol test list 1"), save_protocol("Protocol test list 2")]
    def get():
        return get_items(type='protocol')
    def verify(before, after, response):
        return "protocole" in response.lower() and (str(before) in response or "trouvé" in response.lower())
    return test_action("list_protocols", "liste tous les protocoles", create, get, verify)

def test_all_actions():
    """Test toutes les actions"""
    print("\n" + "="*60)
    print("TESTS COMPLETS DE TOUTES LES ACTIONS MÉMOIRE")
    print("="*60)
    
    tests = [
        ("save_note", test_save_note),
        ("list_notes", test_list_notes),
        ("save_todo", test_save_todo),
        ("list_todos", test_list_todos),
        ("delete_all_notes", test_delete_all_notes),
        ("delete_all_todos", test_delete_all_todos),
        ("save_process", test_save_process),
        ("list_processes", test_list_processes),
        ("save_protocol", test_save_protocol),
        ("list_protocols", test_list_protocols),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Erreur dans {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ COMPLET")
    print("="*60)
    for name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{name:25} : {status}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    print(f"\n{passed}/{total} tests réussis")
    
    if passed == total:
        print("✅ TOUS LES TESTS SONT PASSÉS")
    else:
        print(f"❌ {total - passed} test(s) ont échoué")
    print("="*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = test_all_actions()
    sys.exit(0 if success else 1)

