# Tests pour Memory Helpers
"""
Tests unitaires pour les helpers typés de mémoire
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.memory_core import init_db, get_items
from memory.helpers import save_note, save_todo, save_process, save_protocol


class TestMemoryHelpers(unittest.TestCase):
    """Tests des Memory Helpers"""
    
    def setUp(self):
        """Prépare l'environnement de test"""
        # Créer un fichier DB temporaire
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Créer un schéma temporaire
        self.temp_dir = tempfile.mkdtemp()
        schema_path = Path(self.temp_dir) / "schema.sql"
        with open(schema_path, 'w') as f:
            f.write("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
            """)
        
        # Initialiser la DB
        init_db(db_path=self.db_path, schema_path=str(schema_path))
    
    def tearDown(self):
        """Nettoie après les tests"""
        os.unlink(self.db_path)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_todo(self):
        """Test sauvegarde de todo"""
        todo_id = save_todo("Appeler le fournisseur", tags=["urgent"], db_path=self.db_path)
        self.assertIsInstance(todo_id, int)
        
        # Vérifier présence
        items = get_items(type="todo", db_path=self.db_path)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['content'], "Appeler le fournisseur")
        self.assertEqual(items[0]['type'], "todo")
    
    def test_save_process(self):
        """Test sauvegarde de processus"""
        process_id = save_process(
            "Procédure de vérification fournisseur: 1) Check email 2) Check historique",
            tags=["fournisseur"],
            db_path=self.db_path
        )
        self.assertIsInstance(process_id, int)
        
        # Vérifier présence
        items = get_items(type="process", db_path=self.db_path)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['type'], "process")
    
    def test_save_protocol(self):
        """Test sauvegarde de protocole"""
        protocol_id = save_protocol(
            "Protocole mails fournisseurs: toujours être courtois et confirmer réception",
            tags=["communication"],
            db_path=self.db_path
        )
        self.assertIsInstance(protocol_id, int)
        
        # Vérifier présence
        items = get_items(type="protocol", db_path=self.db_path)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['type'], "protocol")
    
    def test_multiple_types_coexist(self):
        """Test que plusieurs types peuvent coexister"""
        save_note("Note test", db_path=self.db_path)
        save_todo("Todo test", db_path=self.db_path)
        save_process("Process test", db_path=self.db_path)
        save_protocol("Protocol test", db_path=self.db_path)
        
        # Vérifier chaque type
        notes = get_items(type="note", db_path=self.db_path)
        todos = get_items(type="todo", db_path=self.db_path)
        processes = get_items(type="process", db_path=self.db_path)
        protocols = get_items(type="protocol", db_path=self.db_path)
        
        self.assertEqual(len(notes), 1)
        self.assertEqual(len(todos), 1)
        self.assertEqual(len(processes), 1)
        self.assertEqual(len(protocols), 1)
        
        # Vérifier total
        all_items = get_items(db_path=self.db_path)
        self.assertEqual(len(all_items), 4)


if __name__ == '__main__':
    unittest.main()

