import tempfile
import unittest
import shutil
from effortless import EffortlessDB, EffortlessConfig, Field, Query
import effortless
import os


class TestDocs(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_effortless_usage(self):
        db = effortless.db
        db.wipe(wipe_readonly=True)

        # Add items to the database
        db.add({"name": "Alice", "age": 30})
        db.add({"name": "Bob", "age": 25})

        # Get all items from the DB
        all_items = db.get_all()
        self.assertEqual(
            all_items,
            {"1": {"name": "Alice", "age": 30}, "2": {"name": "Bob", "age": 25}},
        )

        # Get items based on a field
        result = db.filter(Field("name").equals("Alice"))
        self.assertEqual(result, {"1": {"name": "Alice", "age": 30}})

        # Wipe the database
        db.wipe()
        self.assertEqual(db.get_all(), {})

    def test_basic_usage(self):
        # Create a new Effortless instance
        db = EffortlessDB()
        db.wipe(wipe_readonly=True)

        # Add items to the database
        db.add({"name": "Charlie", "age": 35})
        db.add({"name": "David", "age": 28})

        # Filter items
        result = db.filter(Field("age").greater_than(30))
        self.assertEqual(result, {"1": {"name": "Charlie", "age": 35}})

    def test_advanced_usage(self):
        # Create a new Effortless instance with a custom directory
        db = EffortlessDB("advanced_db")
        db.set_directory(self.test_dir)
        db.wipe()

        # Add multiple items
        db.add(
            {
                "id": 1,
                "name": "Eve",
                "skills": ["Python", "JavaScript"],
                "joined": "2023-01-15",
            }
        )
        db.add(
            {
                "id": 2,
                "name": "Frank",
                "skills": ["Java", "C++"],
                "joined": "2023-02-20",
            }
        )
        db.add(
            {
                "id": 3,
                "name": "Grace",
                "skills": ["Python", "Ruby"],
                "joined": "2023-03-10",
            }
        )

        # Complex filtering
        python_devs = db.filter(
            Field("skills").contains("Python")
            & Field("joined").between_dates("2023-01-01", "2023-02-28")
        )
        self.assertEqual(len(python_devs), 1)
        self.assertEqual(python_devs["1"]["name"], "Eve")

        # Custom query using Query class
        custom_query = Query(
            lambda item: len(item["skills"]) > 1 and "Python" in item["skills"]
        )
        multi_skill_python_devs = db.filter(custom_query)
        self.assertEqual(len(multi_skill_python_devs), 2)
        self.assertIn("1", multi_skill_python_devs)
        self.assertIn("3", multi_skill_python_devs)

        # Update configuration
        db.configure(EffortlessConfig({"ro": True}))
        with self.assertRaises(Exception):  # The exact exception type may vary
            db.add({"Anything": "will not work"})

    def test_new_filtering_capabilities(self):
        db = EffortlessDB()
        db.wipe(wipe_readonly=True)

        db.add({"name": "Alice", "age": 30, "skills": ["Python", "JavaScript"]})
        db.add({"name": "Bob", "age": 25, "skills": ["Java"]})
        db.add({"name": "Charlie", "age": 35, "skills": ["Python", "Ruby"]})

        # Complex query
        result = db.filter(
            (Field("age").greater_than(25) & Field("skills").contains("Python"))
            | Field("name").startswith("A")
        )
        self.assertEqual(len(result), 2)
        self.assertIn("1", result)
        self.assertIn("3", result)

        # passes method
        def is_experienced(skills):
            return len(skills) > 1

        result = db.filter(Field("skills").passes(is_experienced))
        self.assertEqual(len(result), 2)
        self.assertIn("1", result)
        self.assertIn("3", result)

        # is_type method
        result = db.filter(Field("age").is_type(int))
        self.assertEqual(len(result), 3)

    def test_safety_first(self):
        db = EffortlessDB()
        db.wipe(wipe_readonly=True)

        new_configuration = EffortlessConfig()
        new_configuration.backup = self.test_dir
        db.configure(new_configuration)

        # Add some data
        db.add({"name": "Test", "value": 123})

        # wait for all threads in the db to complete
        db.finish_backup()

        self.assertEqual(db.config.backup, self.test_dir)

        # Check if backup file is created (this is a simplified check)

        backup_files = [
            f for f in os.listdir(self.test_dir) if f.endswith(".effortless")
        ]
        self.assertGreater(len(backup_files), 0)

    def test_powerful_querying(self):
        db = EffortlessDB()
        db.wipe(wipe_readonly=True)

        db.add(
            {
                "username": "bboonstra",
                "known_programming_languages": ["Python", "JavaScript", "Ruby"],
            }
        )
        db.add({"username": "user1", "known_programming_languages": ["Python", "Java"]})
        db.add(
            {
                "username": "user2",
                "known_programming_languages": [
                    "C++",
                    "Java",
                    "Rust",
                    "Go",
                    "Python",
                    "JavaScript",
                ],
            }
        )

        is_bboonstra = Field("username").equals("bboonstra")
        is_experienced = Field("known_programming_languages").passes(
            lambda langs: len(langs) > 5
        )
        GOATs = db.filter(is_bboonstra | is_experienced)

        self.assertEqual(len(GOATs), 2)
        self.assertIn("1", GOATs)
        self.assertIn("3", GOATs)


if __name__ == "__main__":
    unittest.main()
