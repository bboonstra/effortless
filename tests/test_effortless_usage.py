import shutil
import tempfile
import unittest
from effortless import db
from effortless.effortless import DEFAULT_CONFIGURATION


class TestEffortlessUsage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        db.set_directory(self.test_dir)
        db.set_storage("test_db")
        db.wipe()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_set_directory(self):
        with self.assertRaises(TypeError):
            db.set_directory(123)
        with self.assertRaises(ValueError):
            db.set_directory("")
        with self.assertRaises(ValueError):
            db.set_directory("/non/existent/path")

        new_dir = tempfile.mkdtemp()
        db.set_directory(new_dir)
        self.assertEqual(db._storage_directory, new_dir)
        shutil.rmtree(new_dir, ignore_errors=True)

    def test_set_storage(self):
        with self.assertRaises(TypeError):
            db.set_storage(123)
        with self.assertRaises(ValueError):
            db.set_storage("")
        with self.assertRaises(ValueError):
            db.set_storage("invalid name!")

        db.set_storage("new_db")
        self.assertEqual(db._storage_filename, "new_db.effortless")

    def test_search(self):
        db.wipe()
        db.add({"id": 1, "name": "Alice"})
        db.add({"id": 2, "name": "Bob"})

        result = db.search({"name": "Alice"})
        self.assertEqual(result, {'1': {'id': 1, 'name': 'Alice'}})

        result = db.search({"id": 2})
        self.assertEqual(result, {'2': {'id': 2, 'name': 'Bob'}})

        result = db.search({"name": "Charlie"})
        self.assertEqual(result, {})

    def test_add(self):
        db.wipe()
        db.add({"id": 1, "name": "Alice"})
        data = db.get_all()
        self.assertEqual(
            data, {"1": {"id": 1, "name": "Alice"}}
        )

        db.add({"id": 2, "name": "Bob"})
        data = db.get_all()
        self.assertEqual(
            data,
            {
                "1": {"id": 1, "name": "Alice"},
                "2": {"id": 2, "name": "Bob"},
            },
        )

    def test_add_to_dict(self):
        db.wipe()
        db.add({"key": "value"})
        db.add({"new_key": "new_value"})
        data = db.get_all()
        self.assertEqual(
            data,
            {
                "1": {"key": "value"},
                "2": {"new_key": "new_value"},
            },
        )

        with self.assertRaises(TypeError):
            db.add("invalid")

    def test_wipe(self):
        db.add({"test": True})
        db.wipe()
        self.assertEqual(db._read_db(), {"0": DEFAULT_CONFIGURATION})

    def test_read_write_db(self):
        test_data = {
            "0": DEFAULT_CONFIGURATION,
            "1": {"test": True, "nested": {"key": "value"}},
        }
        db._write_db(test_data)
        read_data = db._read_db()
        self.assertEqual(test_data, read_data)

    def test_non_existent_db(self):
        db.set_storage("non_existent")
        self.assertEqual(db._read_db(), {"0": DEFAULT_CONFIGURATION})

if __name__ == "__main__":
    unittest.main()
