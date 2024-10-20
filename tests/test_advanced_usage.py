import tempfile
import unittest
import shutil
import json
import os
import time
from effortless import EffortlessDB, EffortlessConfig, Field


class TestAdvancedUsage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = EffortlessDB()
        self.db.set_directory(self.test_dir)
        self.db.set_storage("test_db")
        self.db.wipe()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_set_directory(self):
        with self.assertRaises(TypeError):
            self.db.set_directory(123)  # type: ignore
        with self.assertRaises(ValueError):
            self.db.set_directory("")
        with self.assertRaises(ValueError):
            self.db.set_directory("/non/existent/path")

        new_dir = tempfile.mkdtemp()
        self.db.set_directory(new_dir)
        self.assertEqual(self.db._storage_directory, new_dir)
        shutil.rmtree(new_dir, ignore_errors=True)

    def test_set_storage(self):
        with self.assertRaises(TypeError):
            self.db.set_storage(123)  # type: ignore
        with self.assertRaises(ValueError):
            self.db.set_storage("")
        with self.assertRaises(ValueError):
            self.db.set_storage("invalid name!")

        self.db.set_storage("new_db")
        self.assertEqual(self.db._storage_filename, "new_db.effortless")

    def test_filter(self):
        self.db.wipe()
        self.db.add({"id": 1, "name": "Alice"})
        self.db.add({"id": 2, "name": "Bob"})

        result = self.db.filter(Field("name").equals("Alice"))
        self.assertEqual(result, {"1": {"id": 1, "name": "Alice"}})

        result = self.db.filter(Field("id").equals(2))
        self.assertEqual(result, {"2": {"id": 2, "name": "Bob"}})

        result = self.db.filter(Field("name").equals("Charlie"))
        self.assertEqual(result, {})

    def test_add(self):
        self.db.wipe()
        self.db.add({"id": 1, "name": "Alice"})
        data = self.db.get_all()
        self.assertEqual(data, {"1": {"id": 1, "name": "Alice"}})

        self.db.add({"id": 2, "name": "Bob"})
        data = self.db.get_all()
        self.assertEqual(
            data,
            {
                "1": {"id": 1, "name": "Alice"},
                "2": {"id": 2, "name": "Bob"},
            },
        )

    def test_wipe(self):
        self.db.add({"test": True})
        self.db.wipe()
        self.assertEqual(self.db._read_db(), EffortlessDB.default_db())

    def test_read_write_db(self):
        test_data = {
            "headers": EffortlessConfig().to_dict(),
            "content": {"test": True, "nested": {"key": "value"}},
        }
        self.db._write_db(test_data)
        read_data = self.db._read_db()
        self.assertEqual(test_data, read_data)

    def test_non_existent_db(self):
        self.db.set_storage("non_existent")
        self.assertEqual(self.db._read_db(), EffortlessDB.default_db())

    def test_search_in_list(self):
        self.db.wipe()
        self.db.add({"id": 1, "name": "Eve", "skills": ["Python", "JavaScript"]})
        self.db.add({"id": 2, "name": "Frank", "skills": ["Java", "C++"]})
        self.db.add({"id": 3, "name": "Grace", "skills": ["Python", "Ruby"]})

        python_devs = self.db.filter(Field("skills").contains("Python"))
        self.assertEqual(len(python_devs), 2)
        self.assertIn("1", python_devs)
        self.assertIn("3", python_devs)
        self.assertEqual(python_devs["1"]["name"], "Eve")
        self.assertEqual(python_devs["3"]["name"], "Grace")

        java_devs = self.db.filter(Field("skills").contains("Java"))
        self.assertEqual(len(java_devs), 1)
        self.assertIn("2", java_devs)
        self.assertEqual(java_devs["2"]["name"], "Frank")

    def test_encryption_and_compression(self):
        self.db.configure(EffortlessConfig({"enc": True, "cmp": True}))
        self.db.add({"test": "data"})
        data = self.db._read_db()
        self.assertIsInstance(data["content"], dict, "Data should be restored to dict after retrieval.")
        self.assertEqual(data["content"], {'1': {'test': 'data'}}, "Data should be restored to original state after retrieval.")

    def test_encryption(self):
        self.db.configure(EffortlessConfig({"enc": True}))
        original_data = {"sensitive": "information"}
        self.db.add(original_data)
        
        # Read the data back
        retrieved_data = self.db.get_all()
        
        # Check if the retrieved data matches the original
        self.assertEqual(retrieved_data["1"], original_data)
        
        # Check if the data on disk is actually encrypted
        with open(self.db._storage_file, "rb") as f:
            raw_data = f.read()
        
        # The raw data should not contain the plaintext sensitive information
        self.assertNotIn(b"information", raw_data)

    def test_backup(self):
        backup_dir = tempfile.mkdtemp()
        self.db.configure(EffortlessConfig({"bp": backup_dir, "bpi": 1}))
        
        # Add some data
        self.db.add({"test": "backup"})
        
        # Wait a bit to ensure the backup thread has time to run
        time.sleep(1)
        
        # Check if a backup file was created
        backup_files = os.listdir(backup_dir)
        self.assertEqual(len(backup_files), 1)
        
        # Check if the backup file contains the correct data
        backup_path = os.path.join(backup_dir, backup_files[0])
        with open(backup_path, "r") as f:
            backup_data = json.load(f)
        
        self.assertEqual(backup_data["content"]["1"], {"test": "backup"})
        
        # Clean up
        shutil.rmtree(backup_dir)

if __name__ == "__main__":
    unittest.main()
