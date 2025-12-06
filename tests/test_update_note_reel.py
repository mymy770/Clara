#!/usr/bin/env python3
"""
Test réel : Clara peut modifier une note existante
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestrator import Orchestrator
from memory.memory_core import init_db, get_items
from memory.helpers import save_note
from utils.logger import DebugLogger
from datetime import datetime

def test_update_note():
    """Test réel : modifier une note existante"""
    print("\n=== TEST RÉEL : Clara modifie une note existante ===")
    
    init_db()
    orchestrator = Orchestrator()
    session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    debug_logger = DebugLogger(session_id)
    
    # Créer une note
    note_id = save_note("Appeler ma femme à 18h")
    print(f"✓ Note créée: ID {note_id}")
    
    # Vérifier la note
    notes_before = get_items(type='note', item_ids=[note_id])
    print(f"✓ Note avant: {notes_before[0]['content']}")
    
    # Demander à Clara d'ajouter du contenu à la note
    response = orchestrator.handle_message(f"rajoute aussi appeler mes enfants dans la note {note_id}", session_id, debug_logger)
    response_text = response.get('response', '')
    print(f"✓ Réponse Clara: {response_text[:150]}")
    
    # Vérifier que la note a été modifiée
    notes_after = get_items(type='note', item_ids=[note_id])
    if notes_after:
        print(f"✓ Note après: {notes_after[0]['content']}")
        
        if "enfants" in notes_after[0]['content'].lower() and "femme" in notes_after[0]['content'].lower():
            print("✅ SUCCÈS : Note modifiée correctement")
            return True
        else:
            print(f"❌ ÉCHEC : Contenu incorrect")
            return False
    else:
        print("❌ ÉCHEC : Note non trouvée")
        return False

if __name__ == "__main__":
    success = test_update_note()
    sys.exit(0 if success else 1)

