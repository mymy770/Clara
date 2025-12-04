"""
Tests pour Memory Core
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.memory_core import MemoryCore


class TestMemoryCore(unittest.TestCase):
    """Tests du Memory Core"""
    
    def setUp(self):
        """Prépare l'environnement de test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Copier le schéma dans un dossier temporaire
        self.temp_dir = tempfile.mkdtemp()
        schema_src = Path(__file__).parent.parent / "memory" / "schema.sql"
        schema_dst = Path(self.temp_dir) / "schema.sql"
        
        if schema_src.exists():
            import shutil
            shutil.copy(schema_src, schema_dst)
        
        self.memory = MemoryCore(db_path=self.temp_db.name)
    
    def tearDown(self):
        """Nettoie après les tests"""
        self.memory.close()
        os.unlink(self.temp_db.name)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_add_and_get_contact(self):
        """Test ajout et récupération de contact"""
        contact_id = self.memory.add_contact(
            name="Jean Dupont",
            phone="+33612345678",
            email="jean@example.com",
            relation="ami"
        )
        
        contact = self.memory.get_contact(contact_id)
        self.assertIsNotNone(contact)
        self.assertEqual(contact['name'], "Jean Dupont")
        self.assertEqual(contact['phone'], "+33612345678")
    
    def test_preferences(self):
        """Test gestion des préférences"""
        self.memory.set_preference("langue", "français", scope="global")
        
        value = self.memory.get_preference("langue", scope="global")
        self.assertEqual(value, "français")
    
    def test_memory_event(self):
        """Test enregistrement d'événement mémoire"""
        session_id = "test_session_001"
        event_id = self.memory.add_memory_event(
            session_id=session_id,
            event_type="test",
            content="Événement de test",
            importance=7
        )
        
        events = self.memory.get_session_events(session_id)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['content'], "Événement de test")


if __name__ == '__main__':
    unittest.main()

