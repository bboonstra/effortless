import tempfile
import unittest
import shutil
from effortless import EffortlessDB, EffortlessConfig, Field
import effortless


class TestDocs(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_effortless_usage(self):
        db = (
            effortless.db
        )  # Same as from effortless import db, but trying not to clog namespace with db and effortless
        db.wipe(wipe_readonly=True)

        # Add items to the database
        db.add({"name": "Alice", "age": 30})
        db.add({"name": "Bob", "age": 25})

        # Search for items
        result = db.filter(Field("name").equals("Alice"))
        self.assertEqual(result, {"1": {"name": "Alice", "age": 30}})

        # Get all items
        all_items = db.get_all()
        self.assertEqual(
            all_items,
            {"1": {"name": "Alice", "age": 30}, "2": {"name": "Bob", "age": 25}},
        )

    def test_basic_usage(self):
        # Create a new Effortless instance
        local_db = EffortlessDB()
        local_db.wipe(wipe_readonly=True)
        # Add items to the database
        local_db.add({"name": "Charlie", "age": 35})
        local_db.add({"name": "David", "age": 28})

        # Search for items
        result = local_db.filter(Field("age").equals(28))
        self.assertEqual(result, {"2": {"name": "David", "age": 28}})

        # Get all items
        all_items = local_db.get_all()
        self.assertEqual(
            all_items,
            {"1": {"name": "Charlie", "age": 35}, "2": {"name": "David", "age": 28}},
        )

    def test_advanced_usage(self):
        # Create a new EffortlessDB instance with a custom directory
        advanced_db = EffortlessDB("advanced_db")
        advanced_db.set_directory(self.test_dir)
        advanced_db.wipe()

        # Add multiple items
        advanced_db.add({"id": 1, "name": "Eve", "skills": ["Python", "JavaScript"]})
        advanced_db.add({"id": 2, "name": "Frank", "skills": ["Java", "C++"]})
        advanced_db.add({"id": 3, "name": "Grace", "skills": ["Python", "Ruby"]})

        # Complex search
        python_devs = advanced_db.filter(Field("skills").contains("Python"))
        self.assertEqual(
            python_devs,
            {
                "1": {"id": 1, "name": "Eve", "skills": ["Python", "JavaScript"]},
                "3": {"id": 3, "name": "Grace", "skills": ["Python", "Ruby"]},
            },
        )

        # Update configuration
        advanced_db.configure(EffortlessConfig({"index_fields": ["id", "name"]}))

        # Wipe the database
        advanced_db.wipe()
        self.assertEqual(advanced_db.get_all(), {})


if __name__ == "__main__":
    unittest.main()
