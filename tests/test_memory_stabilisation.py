#!/usr/bin/env python3
"""
Tests de stabilisation de la mémoire Clara
Teste toutes les actions mémoire en conditions réelles
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.memory_core import init_db, get_items, delete_item
from memory.helpers import save_note, save_todo, save_process, save_protocol

def test_delete_all_notes():
    """Test : supprimer toutes les notes"""
    print("\n=== Test delete_all_notes ===")
    
    # Initialiser la DB
    init_db()
    
    # Créer quelques notes
    id1 = save_note("Note test 1", tags=["test"])
    id2 = save_note("Note test 2", tags=["test"])
    id3 = save_note("Note test 3", tags=["test"])
    print(f"✓ 3 notes créées (IDs: {id1}, {id2}, {id3})")
    
    # Vérifier qu'elles existent
    notes = get_items(type='note')
    assert len(notes) == 3, f"Attendu 3 notes, trouvé {len(notes)}"
    print(f"✓ {len(notes)} notes trouvées")
    
    # Supprimer toutes les notes
    for note in notes:
        delete_item(note['id'])
    print("✓ Toutes les notes supprimées")
    
    # Vérifier qu'elles sont supprimées
    notes_after = get_items(type='note')
    assert len(notes_after) == 0, f"Attendu 0 notes, trouvé {len(notes_after)}"
    print(f"✓ Vérification : {len(notes_after)} notes restantes (OK)")
    
    print("✅ Test delete_all_notes : RÉUSSI\n")
    return True

def test_delete_all_todos():
    """Test : supprimer tous les todos"""
    print("\n=== Test delete_all_todos ===")
    
    # Initialiser la DB
    init_db()
    
    # Créer quelques todos
    id1 = save_todo("Todo test 1", tags=["test"])
    id2 = save_todo("Todo test 2", tags=["test"])
    id3 = save_todo("Todo test 3", tags=["test"])
    print(f"✓ 3 todos créés (IDs: {id1}, {id2}, {id3})")
    
    # Vérifier qu'ils existent
    todos = get_items(type='todo')
    assert len(todos) == 3, f"Attendu 3 todos, trouvé {len(todos)}"
    print(f"✓ {len(todos)} todos trouvés")
    
    # Supprimer tous les todos
    for todo in todos:
        delete_item(todo['id'])
    print("✓ Tous les todos supprimés")
    
    # Vérifier qu'ils sont supprimés
    todos_after = get_items(type='todo')
    assert len(todos_after) == 0, f"Attendu 0 todos, trouvé {len(todos_after)}"
    print(f"✓ Vérification : {len(todos_after)} todos restants (OK)")
    
    print("✅ Test delete_all_todos : RÉUSSI\n")
    return True

def test_delete_all_processes():
    """Test : supprimer tous les processus"""
    print("\n=== Test delete_all_processes ===")
    
    # Initialiser la DB
    init_db()
    
    # Créer quelques processus
    id1 = save_process("Process test 1", tags=["test"])
    id2 = save_process("Process test 2", tags=["test"])
    print(f"✓ 2 processus créés (IDs: {id1}, {id2})")
    
    # Vérifier qu'ils existent
    processes = get_items(type='process')
    assert len(processes) >= 2, f"Attendu au moins 2 processus, trouvé {len(processes)}"
    print(f"✓ {len(processes)} processus trouvés")
    
    # Supprimer tous les processus
    for proc in processes:
        delete_item(proc['id'])
    print("✓ Tous les processus supprimés")
    
    # Vérifier qu'ils sont supprimés
    processes_after = get_items(type='process')
    assert len(processes_after) == 0, f"Attendu 0 processus, trouvé {len(processes_after)}"
    print(f"✓ Vérification : {len(processes_after)} processus restants (OK)")
    
    print("✅ Test delete_all_processes : RÉUSSI\n")
    return True

def test_delete_all_protocols():
    """Test : supprimer tous les protocoles"""
    print("\n=== Test delete_all_protocols ===")
    
    # Initialiser la DB
    init_db()
    
    # Créer quelques protocoles
    id1 = save_protocol("Protocol test 1", tags=["test"])
    id2 = save_protocol("Protocol test 2", tags=["test"])
    print(f"✓ 2 protocoles créés (IDs: {id1}, {id2})")
    
    # Vérifier qu'ils existent
    protocols = get_items(type='protocol')
    assert len(protocols) >= 2, f"Attendu au moins 2 protocoles, trouvé {len(protocols)}"
    print(f"✓ {len(protocols)} protocoles trouvés")
    
    # Supprimer tous les protocoles
    for proto in protocols:
        delete_item(proto['id'])
    print("✓ Tous les protocoles supprimés")
    
    # Vérifier qu'ils sont supprimés
    protocols_after = get_items(type='protocol')
    assert len(protocols_after) == 0, f"Attendu 0 protocoles, trouvé {len(protocols_after)}"
    print(f"✓ Vérification : {len(protocols_after)} protocoles restants (OK)")
    
    print("✅ Test delete_all_protocols : RÉUSSI\n")
    return True

def test_all_memory_actions():
    """Test complet de toutes les actions mémoire"""
    print("\n" + "="*50)
    print("TESTS COMPLETS DE STABILISATION MÉMOIRE")
    print("="*50)
    
    results = []
    
    try:
        results.append(("delete_all_notes", test_delete_all_notes()))
    except Exception as e:
        print(f"❌ Test delete_all_notes : ÉCHEC - {e}\n")
        results.append(("delete_all_notes", False))
    
    try:
        results.append(("delete_all_todos", test_delete_all_todos()))
    except Exception as e:
        print(f"❌ Test delete_all_todos : ÉCHEC - {e}\n")
        results.append(("delete_all_todos", False))
    
    try:
        results.append(("delete_all_processes", test_delete_all_processes()))
    except Exception as e:
        print(f"❌ Test delete_all_processes : ÉCHEC - {e}\n")
        results.append(("delete_all_processes", False))
    
    try:
        results.append(("delete_all_protocols", test_delete_all_protocols()))
    except Exception as e:
        print(f"❌ Test delete_all_protocols : ÉCHEC - {e}\n")
        results.append(("delete_all_protocols", False))
    
    # Résumé
    print("\n" + "="*50)
    print("RÉSUMÉ DES TESTS")
    print("="*50)
    for name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "="*50)
    if all_passed:
        print("✅ TOUS LES TESTS SONT PASSÉS")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
    print("="*50 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = test_all_memory_actions()
    sys.exit(0 if success else 1)

