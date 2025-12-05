#!/usr/bin/env python3
"""
Script de test manuel automatisé pour Clara
Simule les interactions utilisateur via l'orchestrateur
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestrator import Orchestrator
from utils.logger import DebugLogger
from memory.memory_core import get_items, list_preferences
import sqlite3

def count_db_items():
    """Compte les items dans la DB"""
    conn = sqlite3.connect('memory/memory.sqlite')
    cursor = conn.cursor()
    
    cursor.execute("SELECT type, COUNT(*) FROM memory GROUP BY type")
    memory_counts = dict(cursor.fetchall())
    
    cursor.execute("SELECT COUNT(*) FROM preferences")
    pref_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contacts")
    contact_count = cursor.fetchone()[0]
    
    conn.close()
    return memory_counts, pref_count, contact_count

def main():
    """Exécute les tests manuels"""
    print("=" * 60)
    print("TESTS MANUELS CLARA - Phase 2 Validation")
    print("=" * 60)
    print()
    
    # Initialiser
    debug_logger = DebugLogger('test_manual_validation')
    orchestrator = Orchestrator()
    session_id = 'test_manual_validation'
    
    test_results = []
    
    # Test 1: Note
    print("Test 1: Sauvegarde note...")
    response = orchestrator.handle_message("Sauvegarde une note : demain appeler le plombier", session_id, debug_logger)
    print(f"  Réponse: {response[:100]}...")
    memory_counts, _, _ = count_db_items()
    note_count = memory_counts.get('note', 0)
    test_results.append(("Note sauvegardée", note_count == 1, f"Count: {note_count}"))
    print()
    
    # Test 2: Todo
    print("Test 2: Sauvegarde todo...")
    response = orchestrator.handle_message("Sauvegarde un todo : préparer le dossier pour le banquier", session_id, debug_logger)
    print(f"  Réponse: {response[:100]}...")
    memory_counts, _, _ = count_db_items()
    todo_count = memory_counts.get('todo', 0)
    test_results.append(("Todo sauvegardé", todo_count == 1, f"Count: {todo_count}"))
    print()
    
    # Test 3: Process
    print("Test 3: Sauvegarde process...")
    response = orchestrator.handle_message("Sauvegarde un process : comment je prépare une réunion importante", session_id, debug_logger)
    print(f"  Réponse: {response[:100]}...")
    memory_counts, _, _ = count_db_items()
    process_count = memory_counts.get('process', 0)
    test_results.append(("Process sauvegardé", process_count == 1, f"Count: {process_count}"))
    print()
    
    # Test 4: Protocol
    print("Test 4: Sauvegarde protocol...")
    response = orchestrator.handle_message("Sauvegarde un protocole : ma façon idéale de gérer les mails", session_id, debug_logger)
    print(f"  Réponse: {response[:100]}...")
    memory_counts, _, _ = count_db_items()
    protocol_count = memory_counts.get('protocol', 0)
    test_results.append(("Protocol sauvegardé", protocol_count == 1, f"Count: {protocol_count}"))
    print()
    
    # Test 5: Preference
    print("Test 5: Sauvegarde préférence...")
    response = orchestrator.handle_message("Ajoute une préférence : je préfère les résumés courts pour les mails", session_id, debug_logger)
    print(f"  Réponse: {response[:100]}...")
    _, pref_count, _ = count_db_items()
    test_results.append(("Préférence sauvegardée", pref_count == 1, f"Count: {pref_count}"))
    print()
    
    # Test 6: Contact
    print("Test 6: Sauvegarde contact...")
    response = orchestrator.handle_message("Ajoute un contact : Aurélie, ma femme, numéro +33612345678, email aurelie@example.com, relation : femme", session_id, debug_logger)
    print(f"  Réponse: {response[:100]}...")
    _, _, contact_count = count_db_items()
    test_results.append(("Contact sauvegardé", contact_count == 1, f"Count: {contact_count}"))
    print()
    
    # Test 7-12: Lectures
    print("Test 7: Liste notes...")
    response = orchestrator.handle_message("Montre-moi toutes mes notes", session_id, debug_logger)
    has_note = "plombier" in response.lower() or "note" in response.lower()
    test_results.append(("Liste notes", has_note, f"Response contains note: {has_note}"))
    print(f"  Réponse: {response[:150]}...")
    print()
    
    print("Test 8: Liste todos...")
    response = orchestrator.handle_message("Montre-moi tous mes todos", session_id, debug_logger)
    has_todo = "banquier" in response.lower() or "todo" in response.lower()
    test_results.append(("Liste todos", has_todo, f"Response contains todo: {has_todo}"))
    print(f"  Réponse: {response[:150]}...")
    print()
    
    print("Test 9: Liste process...")
    response = orchestrator.handle_message("Montre-moi tous mes process", session_id, debug_logger)
    has_process = "réunion" in response.lower() or "process" in response.lower()
    test_results.append(("Liste process", has_process, f"Response contains process: {has_process}"))
    print(f"  Réponse: {response[:150]}...")
    print()
    
    print("Test 10: Liste protocols...")
    response = orchestrator.handle_message("Montre-moi tous mes protocoles", session_id, debug_logger)
    has_protocol = "mail" in response.lower() or "protocole" in response.lower()
    test_results.append(("Liste protocols", has_protocol, f"Response contains protocol: {has_protocol}"))
    print(f"  Réponse: {response[:150]}...")
    print()
    
    print("Test 11: Liste préférences...")
    response = orchestrator.handle_message("Montre-moi toutes mes préférences", session_id, debug_logger)
    has_pref = "résumé" in response.lower() or "préférence" in response.lower() or "mail" in response.lower()
    test_results.append(("Liste préférences", has_pref, f"Response contains preference: {has_pref}"))
    print(f"  Réponse: {response[:150]}...")
    print()
    
    print("Test 12: Recherche contact...")
    response = orchestrator.handle_message("Montre-moi la fiche contact d'Aurélie", session_id, debug_logger)
    has_contact = "aurélie" in response.lower() or "contact" in response.lower()
    test_results.append(("Recherche contact", has_contact, f"Response contains contact: {has_contact}"))
    print(f"  Réponse: {response[:150]}...")
    print()
    
    # Résumé
    print("=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    passed = sum(1 for _, ok, _ in test_results if ok)
    total = len(test_results)
    
    for name, ok, detail in test_results:
        status = "✅" if ok else "❌"
        print(f"{status} {name}: {detail}")
    
    print()
    print(f"Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("✅ TOUS LES TESTS PASSENT")
        return 0
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        return 1

if __name__ == '__main__':
    sys.exit(main())

