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
        with self.assertRaises(
            TypeError,
            msg="set_directory should raise TypeError when given a non-string argument",
        ):
            self.db.set_directory(123)  # type: ignore
        with self.assertRaises(
            ValueError,
            msg="set_directory should raise ValueError when given an empty string",
        ):
            self.db.set_directory("")
        with self.assertRaises(
            ValueError,
            msg="set_directory should raise ValueError when given a non-existent path",
        ):
            self.db.set_directory("/non/existent/path")

        new_dir = tempfile.mkdtemp()
        self.db.set_directory(new_dir)
        self.assertEqual(
            self.db._storage_directory,
            new_dir,
            "Storage directory should be updated to the new directory",
        )
        shutil.rmtree(new_dir, ignore_errors=True)

    def test_set_storage(self):
        with self.assertRaises(
            TypeError,
            msg="set_storage should raise TypeError when given a non-string argument",
        ):
            self.db.set_storage(123)  # type: ignore
        with self.assertRaises(
            ValueError,
            msg="set_storage should raise ValueError when given an empty string",
        ):
            self.db.set_storage("")
        with self.assertRaises(
            ValueError,
            msg="set_storage should raise ValueError when given an invalid name",
        ):
            self.db.set_storage("invalid name!")

        self.db.set_storage("new_db")
        self.assertEqual(
            self.db._storage_filename,
            "new_db.effortless",
            "Storage filename should be updated with .effortless extension",
        )

    def test_filter(self):
        self.db.wipe()
        self.db.add({"id": 1, "name": "Alice"})
        self.db.add({"id": 2, "name": "Bob"})

        result = self.db.filter(Field("name").equals("Alice"))
        self.assertEqual(
            result,
            [{"id": 1, "name": "Alice"}],
            "Filter should return only Alice's entry",
        )

        result = self.db.filter(Field("id").equals(2))
        self.assertEqual(
            result, [{"id": 2, "name": "Bob"}], "Filter should return only Bob's entry"
        )

        result = self.db.filter(Field("name").equals("Charlie"))
        self.assertEqual(
            result, [], "Filter should return an empty list for non-existent name"
        )

    def test_add(self):
        self.db.wipe()
        self.db.add({"id": 1, "name": "Alice"})
        data = self.db.get_all()
        self.assertEqual(
            data,
            [{"id": 1, "name": "Alice"}],
            "Database should contain only Alice's entry after adding it",
        )

        self.db.add({"id": 2, "name": "Bob"})
        data = self.db.get_all()
        self.assertEqual(
            data,
            [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
            "Database should contain both Alice's and Bob's entries after adding Bob",
        )

    def test_wipe(self):
        self.db.add({"test": True})
        self.db.wipe()
        self.assertEqual(
            self.db._read_db(),
            EffortlessDB.default_db(),
            "Database should be empty after wiping",
        )

    def test_read_write_db(self):
        test_data = {
            "headers": EffortlessConfig().to_dict(),
            "content": [{"test": True, "nested": {"key": "value"}}],
        }
        self.db._write_db(test_data)
        read_data = self.db._read_db()
        self.assertEqual(
            test_data,
            read_data,
            "Data read from database should match the data written to it",
        )

    def test_non_existent_db(self):
        self.db.set_storage("non_existent")
        self.assertEqual(
            self.db._read_db(),
            EffortlessDB.default_db(),
            "Reading a non-existent database should return the default empty database structure",
        )

    def test_search_in_list(self):
        self.db.wipe()
        self.db.add({"id": 1, "name": "Eve", "skills": ["Python", "JavaScript"]})
        self.db.add({"id": 2, "name": "Frank", "skills": ["Java", "C++"]})
        self.db.add({"id": 3, "name": "Grace", "skills": ["Python", "Ruby"]})

        python_devs = self.db.filter(Field("skills").contains("Python"))
        self.assertEqual(
            len(python_devs), 2, "Filter should return two Python developers"
        )
        self.assertEqual(
            python_devs[0]["name"], "Eve", "First Python developer should be Eve"
        )
        self.assertEqual(
            python_devs[1]["name"], "Grace", "Second Python developer should be Grace"
        )

        java_devs = self.db.filter(Field("skills").contains("Java"))
        self.assertEqual(len(java_devs), 1, "Filter should return one Java developer")
        self.assertEqual(
            java_devs[0]["name"], "Frank", "Java developer should be Frank"
        )

    def test_encryption_and_compression(self):
        self.db.configure(EffortlessConfig({"enc": True, "cmp": True}))
        self.db.add({"test": "data"})
        data = self.db._read_db()
        self.assertIsInstance(
            data["content"],
            list,
            "Data should be restored to list after retrieval with encryption and compression",
        )
        self.assertEqual(
            data["content"],
            [{"test": "data"}],
            "Data should be restored to original state after retrieval with encryption and compression",
        )

    def test_encryption(self):
        self.db.configure(EffortlessConfig({"enc": True}))
        original_data = {"sensitive": "information"}
        self.db.add(original_data)

        retrieved_data = self.db.get_all()
        self.assertEqual(
            retrieved_data[0],
            original_data,
            "Retrieved data should match original data after encryption",
        )

        with open(self.db._storage_file, "rb") as f:
            raw_data = f.read()
        self.assertNotIn(
            b"information",
            raw_data,
            "Raw data should not contain plaintext sensitive information",
        )

    def test_backup(self):
        backup_dir = tempfile.mkdtemp()
        self.db.configure(EffortlessConfig({"bp": backup_dir, "bpi": 1}))

        self.db.add({"test": "backup"})
        time.sleep(1)

        backup_files = os.listdir(backup_dir)
        self.assertEqual(len(backup_files), 1, "One backup file should be created")

        backup_path = os.path.join(backup_dir, backup_files[0])
        with open(backup_path, "r") as f:
            backup_data = json.load(f)

        self.assertEqual(
            backup_data["content"][0],
            {"test": "backup"},
            "Backup file should contain the correct data",
        )

        shutil.rmtree(backup_dir)


if __name__ == "__main__":
    unittest.main()
