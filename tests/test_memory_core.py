# Tests pour Memory Core
"""
Tests unitaires pour l'API mémoire
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.memory_core import init_db, save_item, get_items, search_items, delete_item, update_item


class TestMemoryCore(unittest.TestCase):
    """Tests du Memory Core"""
    
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
    
    def test_save_and_get_item(self):
        """Test sauvegarde et récupération d'item"""
        # Sauvegarder
        item_id = save_item(
            type="note",
            content="Test note",
            tags=["test", "unittest"],
            db_path=self.db_path
        )
        self.assertIsInstance(item_id, int)
        self.assertGreater(item_id, 0)
        
        # Récupérer
        items = get_items(type="note", db_path=self.db_path)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['content'], "Test note")
        self.assertEqual(items[0]['tags'], ["test", "unittest"])
    
    def test_search_items(self):
        """Test recherche d'items"""
        # Sauvegarder plusieurs items
        save_item(type="note", content="Python is great", db_path=self.db_path)
        save_item(type="note", content="JavaScript is cool", db_path=self.db_path)
        save_item(type="note", content="Python for AI", db_path=self.db_path)
        
        # Rechercher
        results = search_items(query="Python", type="note", db_path=self.db_path)
        self.assertEqual(len(results), 2)
    
    def test_delete_item(self):
        """Test suppression d'item"""
        # Sauvegarder
        item_id = save_item(type="note", content="To delete", db_path=self.db_path)
        
        # Vérifier présence
        items = get_items(db_path=self.db_path)
        self.assertEqual(len(items), 1)
        
        # Supprimer
        delete_item(item_id=item_id, db_path=self.db_path)
        
        # Vérifier suppression
        items = get_items(db_path=self.db_path)
        self.assertEqual(len(items), 0)
    
    def test_update_item(self):
        """Test mise à jour d'item"""
        # Sauvegarder
        item_id = save_item(type="note", content="Original", db_path=self.db_path)
        
        # Mettre à jour
        update_item(item_id=item_id, content="Updated", db_path=self.db_path)
        
        # Vérifier
        items = get_items(db_path=self.db_path)
        self.assertEqual(items[0]['content'], "Updated")


if __name__ == '__main__':
    unittest.main()
