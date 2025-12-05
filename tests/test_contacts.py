# Tests pour les contacts
"""
Tests unitaires pour la gestion des contacts
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.memory_core import init_db, get_items
from memory.contacts import save_contact, update_contact, find_contacts, get_all_contacts


class TestContacts(unittest.TestCase):
    """Tests des fonctions contacts"""
    
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
    
    def test_save_contact_minimal(self):
        """Test sauvegarde contact minimal"""
        contact = {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'phones': [
                {'number': '+33612345678', 'label': 'perso', 'primary': True, 'channels': ['call', 'sms']}
            ]
        }
        
        contact_id = save_contact(contact, db_path=self.db_path)
        self.assertIsInstance(contact_id, int)
        
        # Vérifier sauvegarde
        contacts = get_items(type="contact", db_path=self.db_path)
        self.assertEqual(len(contacts), 1)
        
        # Vérifier contenu
        saved_data = json.loads(contacts[0]['content'])
        self.assertEqual(saved_data['first_name'], 'Jean')
        self.assertEqual(saved_data['last_name'], 'Dupont')
    
    def test_save_contact_complet(self):
        """Test sauvegarde contact complet"""
        contact = {
            'first_name': 'Aurélie',
            'last_name': 'Malai',
            'display_name': 'Aurélie Malai',
            'aliases': ['ma femme', 'mon épouse'],
            'category': 'family',
            'relationship': 'wife',
            'phones': [
                {
                    'number': '+972-5x-xxx-xxxx',
                    'label': 'mobile perso',
                    'primary': True,
                    'channels': ['call', 'sms', 'whatsapp']
                }
            ],
            'emails': [
                {
                    'address': 'aurelie@example.com',
                    'label': 'perso',
                    'primary': True
                }
            ],
            'company': 'Active Games',
            'role': 'Associée / co-fondatrice',
            'notes': [
                'Prépare les deals fournisseurs LED',
                'Passeports FR + ISR'
            ]
        }
        
        contact_id = save_contact(contact, db_path=self.db_path)
        
        # Vérifier sauvegarde
        contacts = get_items(type="contact", db_path=self.db_path)
        self.assertEqual(len(contacts), 1)
        
        saved_data = json.loads(contacts[0]['content'])
        self.assertEqual(saved_data['first_name'], 'Aurélie')
        self.assertEqual(len(saved_data['aliases']), 2)
        self.assertEqual(saved_data['category'], 'family')
        self.assertEqual(len(saved_data['phones']), 1)
        self.assertEqual(len(saved_data['emails']), 1)
    
    def test_find_contacts_by_name(self):
        """Test recherche contact par nom"""
        save_contact({
            'first_name': 'Marie',
            'last_name': 'Martin',
            'phones': [{'number': '+33612345678', 'label': 'perso', 'primary': True, 'channels': ['call']}]
        }, db_path=self.db_path)
        
        # Rechercher
        results = find_contacts('Marie', db_path=self.db_path)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['first_name'], 'Marie')
    
    def test_find_contacts_by_alias(self):
        """Test recherche contact par alias"""
        save_contact({
            'first_name': 'Paul',
            'last_name': 'Durand',
            'aliases': ['mon frère', 'Paulo'],
            'phones': [{'number': '+33612345678', 'label': 'perso', 'primary': True, 'channels': ['call']}]
        }, db_path=self.db_path)
        
        # Rechercher par alias
        results = find_contacts('mon frère', db_path=self.db_path)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['first_name'], 'Paul')
    
    def test_update_contact(self):
        """Test mise à jour contact"""
        # Créer
        contact_id = save_contact({
            'first_name': 'Test',
            'last_name': 'User',
            'phones': [{'number': '+33600000000', 'label': 'perso', 'primary': True, 'channels': ['call']}]
        }, db_path=self.db_path)
        
        # Mettre à jour
        update_contact(contact_id, {
            'company': 'TestCorp',
            'role': 'CEO'
        }, db_path=self.db_path)
        
        # Vérifier
        contacts = get_all_contacts(db_path=self.db_path)
        self.assertEqual(contacts[0]['company'], 'TestCorp')
        self.assertEqual(contacts[0]['role'], 'CEO')


if __name__ == '__main__':
    unittest.main()

