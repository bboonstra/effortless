import shutil
import tempfile
import unittest
from effortless import db, EffortlessDB, EffortlessConfig
from effortless.search import Field


class TestEffortlessUsage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        db.set_directory(self.test_dir)
        db.set_storage("test_db")
        db.wipe()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_set_directory(self):
        with self.assertRaises(
            TypeError,
            msg="set_directory should raise TypeError when given a non-string argument",
        ):
            db.set_directory(123)  # type: ignore
        with self.assertRaises(
            ValueError,
            msg="set_directory should raise ValueError when given an empty string",
        ):
            db.set_directory("")
        with self.assertRaises(
            ValueError,
            msg="set_directory should raise ValueError when given a non-existent path",
        ):
            db.set_directory("/non/existent/path")

        new_dir = tempfile.mkdtemp()
        db.set_directory(new_dir)
        self.assertEqual(
            db._storage_directory,
            new_dir,
            "Storage directory should be updated to the new directory",
        )
        shutil.rmtree(new_dir, ignore_errors=True)

    def test_set_storage(self):
        with self.assertRaises(
            TypeError,
            msg="set_storage should raise TypeError when given a non-string argument",
        ):
            db.set_storage(123)  # type: ignore
        with self.assertRaises(
            ValueError,
            msg="set_storage should raise ValueError when given an empty string",
        ):
            db.set_storage("")
        with self.assertRaises(
            ValueError,
            msg="set_storage should raise ValueError when given an invalid name",
        ):
            db.set_storage("invalid name!")

        db.set_storage("new_db")
        self.assertEqual(
            db._storage_filename,
            "new_db.effortless",
            "Storage filename should be updated with .effortless extension",
        )

    def test_search(self):
        db.wipe()
        db.add({"id": 1, "name": "Alice"})
        db.add({"id": 2, "name": "Bob"})

        result = db.filter(query=Field("name").equals("Alice"))
        self.assertEqual(
            result,
            [{"id": 1, "name": "Alice"}],
            "Filter should return only Alice's entry",
        )

        result = db.filter(query=Field("id").equals(2))
        self.assertEqual(
            result, [{"id": 2, "name": "Bob"}], "Filter should return only Bob's entry"
        )

        result = db.filter(query=Field("name").equals("Charlie"))
        self.assertEqual(
            result, [], "Filter should return an empty list for non-existent name"
        )

    def test_add(self):
        db.wipe()
        db.add({"id": 1, "name": "Alice"})
        data = db.get_all()
        self.assertEqual(
            data,
            [{"id": 1, "name": "Alice"}],
            "Database should contain only Alice's entry after adding it",
        )

        db.add({"id": 2, "name": "Bob"})
        data = db.get_all()
        self.assertEqual(
            data,
            [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ],
            "Database should contain both Alice's and Bob's entries after adding Bob",
        )

    def test_add_to_list(self):
        db.wipe()
        db.add({"key": "value"})
        db.add({"new_key": "new_value"})
        data = db.get_all()
        self.assertEqual(
            data,
            [
                {"key": "value"},
                {"new_key": "new_value"},
            ],
            "Database should contain both entries with different keys",
        )

        with self.assertRaises(
            TypeError, msg="add should raise TypeError when given a non-dict argument"
        ):
            db.add("invalid")  # type: ignore

    def test_wipe(self):
        db.add({"test": True})
        db.wipe()
        self.assertEqual(
            db._read_db(),
            EffortlessDB.default_db(),
            "Database should be empty after wiping",
        )

    def test_read_write_db(self):
        test_data = {
            "headers": EffortlessConfig().to_dict(),
            "content": [{"test": True, "nested": {"key": "value"}}],
        }
        db._write_db(test_data)
        read_data = db._read_db()
        self.assertEqual(
            test_data,
            read_data,
            "Data read from database should match the data written to it",
        )

    def test_non_existent_db(self):
        db.set_storage("non_existent")
        self.assertEqual(
            db._read_db(),
            EffortlessDB.default_db(),
            "Reading a non-existent database should return the default empty database structure",
        )


if __name__ == "__main__":
    unittest.main()
