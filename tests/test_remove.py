import unittest
from effortless import EffortlessDB, Field, Query


class TestRemove(unittest.TestCase):
    def setUp(self):
        self.db = EffortlessDB()
        self.db.wipe()
        self.db.add({"id": 1, "name": "Alice", "age": 30})
        self.db.add({"id": 2, "name": "Bob", "age": 25})
        self.db.add({"id": 3, "name": "Charlie", "age": 35})
        self.db.add({"id": 4, "name": "David", "age": 40})
        self.db.add({"id": 5, "name": "Eve", "age": 28})

    def test_remove_single_entry(self):
        result = self.db.remove(Field("name").equals("Alice"))
        self.assertTrue(result, "Remove operation should return True when successful")
        self.assertEqual(
            len(self.db.get_all()), 4, "Database should have 4 entries after removal"
        )
        self.assertFalse(
            any(entry["name"] == "Alice" for entry in self.db.get_all()),
            "Alice should no longer be in the database",
        )

    def test_remove_no_match(self):
        result = self.db.remove(Field("name").equals("Frank"))
        self.assertFalse(
            result, "Remove operation should return False when no match is found"
        )
        self.assertEqual(
            len(self.db.get_all()), 5, "Database should still have 5 entries"
        )

    def test_remove_multiple_matches(self):
        self.db.add({"id": 6, "name": "Alice", "age": 22})
        with self.assertRaises(
            ValueError,
            msg="Remove should raise ValueError when multiple matches are found",
        ):
            self.db.remove(Field("name").equals("Alice"))

    def test_remove_with_complex_condition(self):
        result = self.db.remove(
            Query(lambda x: x["name"].startswith("D") and x["age"] > 35)
        )
        self.assertTrue(
            result, "Remove with complex condition should return True when successful"
        )
        self.assertEqual(
            len(self.db.get_all()), 4, "Database should have 4 entries after removal"
        )
        self.assertFalse(
            any(entry["name"] == "David" for entry in self.db.get_all()),
            "David should no longer be in the database",
        )

    def test_erase_single_entry(self):
        result = self.db.erase(Field("name").equals("Bob"))
        self.assertEqual(result, 1, "Erase should return 1 for a single entry removed")
        self.assertEqual(
            len(self.db.get_all()), 4, "Database should have 4 entries after erasure"
        )
        self.assertFalse(
            any(entry["name"] == "Bob" for entry in self.db.get_all()),
            "Bob should no longer be in the database",
        )

    def test_erase_multiple_entries(self):
        result = self.db.erase(Field("age").less_than(30))
        self.assertEqual(result, 2, "Erase should return 2 for two entries removed")
        self.assertEqual(
            len(self.db.get_all()), 3, "Database should have 3 entries after erasure"
        )
        self.assertFalse(
            any(entry["age"] < 30 for entry in self.db.get_all()),
            "No entries with age < 30 should remain",
        )

    def test_erase_no_match(self):
        result = self.db.erase(Field("age").greater_than(50))
        self.assertEqual(result, 0, "Erase should return 0 when no entries match")
        self.assertEqual(
            len(self.db.get_all()), 5, "Database should still have 5 entries"
        )

    def test_erase_all_entries(self):
        result = self.db.erase(Query(lambda x: True))
        self.assertEqual(result, 5, "Erase should return 5 for all entries removed")
        self.assertEqual(
            len(self.db.get_all()),
            0,
            "Database should be empty after erasing all entries",
        )

    def test_erase_with_complex_condition(self):
        result = self.db.erase(
            Query(lambda x: x["age"] % 2 == 0 and x["name"].lower().startswith("d"))
        )
        self.assertEqual(
            result, 1, "Erase with complex condition should remove 1 entry"
        )
        self.assertEqual(
            len(self.db.get_all()), 4, "Database should have 4 entries after erasure"
        )
        self.assertFalse(
            any(entry["name"] == "David" for entry in self.db.get_all()),
            "David should no longer be in the database",
        )

    def test_remove_then_erase(self):
        self.db.remove(Field("name").equals("Alice"))
        result = self.db.erase(Field("age").greater_than(30))
        self.assertEqual(
            result, 2, "Erase should remove 2 entries after previous removal"
        )
        self.assertEqual(
            len(self.db.get_all()), 2, "Database should have 2 entries after operations"
        )
        self.assertTrue(
            all(entry["age"] <= 30 for entry in self.db.get_all()),
            "All remaining entries should have age <= 30",
        )

    def test_erase_then_remove(self):
        self.db.erase(Field("age").less_than(30))
        result = self.db.remove(Field("name").equals("Charlie"))
        self.assertTrue(result, "Remove should be successful after previous erasure")
        self.assertEqual(
            len(self.db.get_all()), 2, "Database should have 2 entries after operations"
        )
        self.assertTrue(
            all(entry["age"] >= 30 for entry in self.db.get_all()),
            "All remaining entries should have age >= 30",
        )

    def test_remove_last_entry(self):
        self.db.erase(Query(lambda x: x["id"] != 5))
        result = self.db.remove(Field("name").equals("Eve"))
        self.assertTrue(result, "Remove should be successful for last entry")
        self.assertEqual(
            len(self.db.get_all()),
            0,
            "Database should be empty after removing last entry",
        )

    def test_erase_with_field_not_present_in_all_entries(self):
        self.db.add({"id": 6, "name": "Frank", "age": 45, "city": "New York"})
        result = self.db.erase(Field("city").equals("New York"))
        self.assertEqual(result, 1, "Erase should remove 1 entry with matching city")
        self.assertEqual(
            len(self.db.get_all()), 5, "Database should have 5 entries after erasure"
        )
        self.assertFalse(
            any(entry.get("city") == "New York" for entry in self.db.get_all()),
            "No entries with city 'New York' should remain",
        )

    def test_remove_with_case_insensitive_condition(self):
        result = self.db.remove(Query(lambda x: x["name"].lower() == "charlie"))
        self.assertTrue(
            result, "Remove with case-insensitive condition should be successful"
        )
        self.assertEqual(
            len(self.db.get_all()), 4, "Database should have 4 entries after removal"
        )
        self.assertFalse(
            any(entry["name"].lower() == "charlie" for entry in self.db.get_all()),
            "Charlie should no longer be in the database",
        )

    def test_erase_with_multiple_conditions(self):
        result = self.db.erase(
            Query(lambda x: x["age"] > 25 and x["name"].startswith("C"))
        )
        self.assertEqual(
            result, 1, "Erase with multiple conditions should remove 1 entry"
        )
        self.assertEqual(
            len(self.db.get_all()), 4, "Database should have 4 entries after erasure"
        )
        self.assertFalse(
            any(entry["name"] == "Charlie" for entry in self.db.get_all()),
            "Charlie should no longer be in the database",
        )

    # Additional tests for increased coverage

    def test_remove_with_numeric_condition(self):
        result = self.db.remove(Field("age").equals(40))
        self.assertTrue(result, "Remove with numeric condition should be successful")
        self.assertEqual(
            len(self.db.get_all()), 4, "Database should have 4 entries after removal"
        )
        self.assertFalse(
            any(entry["age"] == 40 for entry in self.db.get_all()),
            "No entries with age 40 should remain",
        )

    def test_erase_with_range_condition(self):
        result = self.db.erase(Query(lambda x: 25 <= x["age"] <= 35))
        self.assertEqual(
            result, 4, "Erase with range condition should remove 4 entries"
        )
        self.assertEqual(
            len(self.db.get_all()), 1, "Database should have 1 entry after erasure"
        )
        self.assertTrue(
            all(entry["age"] < 25 or entry["age"] > 35 for entry in self.db.get_all()),
            "All remaining entries should have age outside the range 25-35",
        )

    def test_remove_with_non_existent_field(self):
        self.db.wipe()
        self.db.add({"id": 1, "name": "Alice", "age": 30})
        self.db.add({"id": 2, "name": "Bob", "age": 25})
        self.db.add({"id": 3, "name": "Charlie", "age": 35})
        self.db.add({"id": 4, "name": "David", "age": 40})
        self.db.add({"id": 5, "name": "Eve", "age": 28})
        result = self.db.remove(Field("salary").greater_than(50000))
        self.assertFalse(result, "Remove with non-existent field should return False")
        self.assertEqual(
            len(self.db.get_all()), 5, "Database should still have 5 entries"
        )

    def test_erase_with_complex_query_and_multiple_fields(self):
        self.db.add(
            {"id": 6, "name": "Frank", "age": 45, "city": "New York", "salary": 60000}
        )
        result = self.db.erase(
            Query(lambda x: x["age"] > 40 and x.get("salary", 0) > 55000)
        )
        self.assertEqual(
            result,
            1,
            "Erase with complex query and multiple fields should remove 1 entry",
        )
        self.assertEqual(
            len(self.db.get_all()), 5, "Database should have 5 entries after erasure"
        )
        self.assertFalse(
            any(entry.get("name") == "Frank" for entry in self.db.get_all()),
            "Frank should no longer be in the database",
        )


if __name__ == "__main__":
    unittest.main()
