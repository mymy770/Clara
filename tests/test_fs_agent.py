"""
Tests pour le FS Agent
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.fs_agent import FSAgent
from drivers.fs_driver import FSDriver


class TestFSAgent(unittest.TestCase):
    """Tests du FS Agent"""
    
    def setUp(self):
        """Prépare l'environnement de test"""
        self.temp_dir = tempfile.mkdtemp()
        self.driver = FSDriver(base_path=self.temp_dir)
        self.agent = FSAgent(config={}, fs_driver=self.driver)
    
    def tearDown(self):
        """Nettoie après les tests"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_write_and_read_file(self):
        """Test écriture et lecture de fichier"""
        test_content = "Contenu de test"
        test_file = "test.txt"
        
        # Écriture
        result = self.agent.write_file(test_file, test_content)
        self.assertTrue(result)
        
        # Lecture
        content = self.agent.read_file(test_file)
        self.assertEqual(content, test_content)
    
    def test_list_directory(self):
        """Test listing de répertoire"""
        # Créer quelques fichiers
        self.agent.write_file("file1.txt", "contenu 1")
        self.agent.write_file("file2.txt", "contenu 2")
        
        # Lister
        files = self.agent.list_directory(".")
        self.assertIn("file1.txt", files)
        self.assertIn("file2.txt", files)


if __name__ == '__main__':
    unittest.main()

