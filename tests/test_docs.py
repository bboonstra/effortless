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

        # Add entries to the database
        db.add({"name": "Alice", "age": 30})
        db.add({"name": "Bob", "age": 25})

        # Get all entries from the DB
        all_entries = db.get_all()
        self.assertEqual(
            all_entries,
            [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
            "get_all() should return all entries added to the database",
        )

        # Get entries based on a field
        result = db.filter(Field("name").equals("Alice"))
        self.assertEqual(
            result,
            [{"name": "Alice", "age": 30}],
            "filter() should return only Alice's entry when filtering by name",
        )

        # Wipe the database
        db.wipe()
        self.assertEqual(db.get_all(), [], "Database should be empty after wiping")

    def test_basic_usage(self):
        # Create a new Effortless instance
        db = EffortlessDB()
        db.wipe(wipe_readonly=True)

        # Add entries to the database
        db.add({"name": "Charlie", "age": 35})
        db.add({"name": "David", "age": 28})

        # Filter entries
        result = db.filter(Field("age").greater_than(30))
        self.assertEqual(
            result,
            [{"name": "Charlie", "age": 35}],
            "filter() should return only Charlie's entry when filtering for age > 30",
        )

    def test_advanced_usage(self):
        # Create a new Effortless instance with a custom directory
        db = EffortlessDB("advanced_db")
        db.set_directory(self.test_dir)
        db.wipe()

        # Add multiple entries
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
        self.assertEqual(
            len(python_devs),
            1,
            "Complex filter should return one Python developer who joined between Jan and Feb 2023",
        )
        self.assertEqual(
            python_devs[0]["name"],
            "Eve",
            "The Python developer matching the complex filter should be Eve",
        )

        # Custom query using Query class
        custom_query = Query(
            lambda entry: len(entry["skills"]) > 1 and "Python" in entry["skills"]
        )
        multi_skill_python_devs = db.filter(custom_query)
        self.assertEqual(
            len(multi_skill_python_devs),
            2,
            "Custom query should return two developers with multiple skills including Python",
        )
        self.assertEqual(
            multi_skill_python_devs[0]["name"],
            "Eve",
            "First developer matching custom query should be Eve",
        )
        self.assertEqual(
            multi_skill_python_devs[1]["name"],
            "Grace",
            "Second developer matching custom query should be Grace",
        )

        # Update configuration
        db.configure(EffortlessConfig({"ro": True}))
        with self.assertRaises(
            Exception, msg="Adding to a read-only database should raise an exception"
        ):
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
        self.assertEqual(
            len(result),
            2,
            "Complex query should return two entries (Alice and Charlie)",
        )
        self.assertEqual(
            result[0]["name"], "Alice", "First result of complex query should be Alice"
        )
        self.assertEqual(
            result[1]["name"],
            "Charlie",
            "Second result of complex query should be Charlie",
        )

        # passes method
        def is_experienced(skills):
            return len(skills) > 1

        result = db.filter(Field("skills").passes(is_experienced))
        self.assertEqual(
            len(result),
            2,
            "Filter with passes() method should return two entries (Alice and Charlie)",
        )
        self.assertEqual(
            result[0]["name"],
            "Alice",
            "First result of passes() filter should be Alice",
        )
        self.assertEqual(
            result[1]["name"],
            "Charlie",
            "Second result of passes() filter should be Charlie",
        )

        # is_type method
        result = db.filter(Field("age").is_type(int))
        self.assertEqual(
            len(result),
            3,
            "Filter with is_type() method should return all three entries",
        )

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

        self.assertEqual(
            db.config.backup,
            self.test_dir,
            "Database backup directory should be set to the test directory",
        )

        # Check if backup file is created (this is a simplified check)
        backup_files = [
            f for f in os.listdir(self.test_dir) if f.endswith(".effortless")
        ]
        self.assertGreater(
            len(backup_files),
            0,
            "At least one backup file should be created in the test directory",
        )

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

        self.assertEqual(
            len(GOATs),
            2,
            "Powerful query should return two entries (bboonstra and user2)",
        )
        self.assertEqual(
            GOATs[0]["username"],
            "bboonstra",
            "First result of powerful query should be bboonstra",
        )
        self.assertEqual(
            GOATs[1]["username"],
            "user2",
            "Second result of powerful query should be user2",
        )


if __name__ == "__main__":
    unittest.main()
