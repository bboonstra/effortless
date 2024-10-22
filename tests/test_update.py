import unittest
from effortless import EffortlessDB, Field, Query


class TestUpdate(unittest.TestCase):
    def setUp(self):
        self.db = EffortlessDB()
        self.db.wipe()
        self.db.add({"id": 1, "name": "Alice", "age": 30})
        self.db.add({"id": 2, "name": "Bob", "age": 25})
        self.db.add({"id": 3, "name": "Charlie", "age": 35})

    def test_update_single_entry(self):
        result = self.db.update({"age": 31}, Field("name").equals("Alice"))
        self.assertTrue(result)
        updated_entry = self.db.filter(Field("name").equals("Alice"))[0]
        self.assertEqual(updated_entry["age"], 31)

    def test_update_no_match(self):
        result = self.db.update({"age": 40}, Field("name").equals("David"))
        self.assertFalse(result)

    def test_update_multiple_matches(self):
        self.db.add({"id": 4, "name": "Alice", "age": 28})
        with self.assertRaises(ValueError):
            self.db.update({"age": 32}, Field("name").equals("Alice"))

    def test_batch_update(self):
        result = self.db.batch({"status": "active"}, Field("age").greater_than(25))
        self.assertEqual(result, 2)
        active_entries = self.db.filter(Field("status").equals("active"))
        self.assertEqual(len(active_entries), 2)
        self.assertTrue(all(entry["age"] > 25 for entry in active_entries))

    def test_batch_update_no_match(self):
        result = self.db.batch({"status": "inactive"}, Field("age").greater_than(40))
        self.assertEqual(result, 0)

    def test_batch_update_all(self):
        result = self.db.batch({"verified": True}, Query(lambda x: True))
        self.assertEqual(result, 3)
        all_entries = self.db.get_all()
        self.assertTrue(all(entry.get("verified") for entry in all_entries))

    def test_update_with_new_field(self):
        result = self.db.update({"status": "employed"}, Field("name").equals("Bob"))
        self.assertTrue(result, "Update operation should return True when successful")
        updated_entry = self.db.filter(Field("name").equals("Bob"))[0]
        self.assertEqual(
            updated_entry["status"],
            "employed",
            "New field 'status' should be added with value 'employed'",
        )

    def test_update_with_complex_condition(self):
        result = self.db.update(
            {"category": "senior"},
            Query(lambda x: x["name"].startswith("C") and x["age"] > 30),
        )
        self.assertTrue(
            result, "Update with complex condition should return True when successful"
        )
        updated_entry = self.db.filter(Field("name").equals("Charlie"))[0]
        self.assertEqual(
            updated_entry["category"],
            "senior",
            "Entry matching complex condition should have new 'category' field set to 'senior'",
        )

    def test_update_non_existent_field(self):
        result = self.db.update({"non_existent": 42}, Field("name").equals("Alice"))
        self.assertTrue(result, "Update with non-existent field should return True")
        updated_entry = self.db.filter(Field("name").equals("Alice"))[0]
        self.assertEqual(
            updated_entry["non_existent"],
            42,
            "Non-existent field should be added with the specified value",
        )

    def test_batch_update_with_multiple_fields(self):
        result = self.db.batch(
            {"status": "active", "last_updated": "2023-04-01"},
            Field("age").less_than(35),
        )
        self.assertEqual(
            result, 2, "Batch update should affect 2 entries (Alice and Bob)"
        )
        updated_entries = self.db.filter(Field("status").equals("active"))
        self.assertEqual(
            len(updated_entries), 2, "There should be 2 entries with 'active' status"
        )
        self.assertTrue(
            all(entry["last_updated"] == "2023-04-01" for entry in updated_entries),
            "All updated entries should have 'last_updated' field set to '2023-04-01'",
        )

    def test_batch_update_with_complex_query(self):
        self.db.add({"id": 4, "name": "David", "age": 40, "city": "New York"})
        result = self.db.batch(
            {"category": "special"},
            Query(lambda x: x["age"] > 30 and x.get("city") == "New York"),
        )
        self.assertEqual(
            result, 1, "Batch update with complex query should affect 1 entry (David)"
        )
        updated_entry = self.db.filter(Field("name").equals("David"))[0]
        self.assertEqual(
            updated_entry["category"],
            "special",
            "Entry matching complex query should have 'category' set to 'special'",
        )

    def test_batch_update_with_no_changes(self):
        result = self.db.batch({"age": 30}, Field("age").equals(30))
        self.assertEqual(
            result,
            1,
            "Batch update should report 1 affected entry, even if no actual change",
        )
        unchanged_entry = self.db.filter(Field("name").equals("Alice"))[0]
        self.assertEqual(
            unchanged_entry["age"], 30, "Alice's age should remain 30 after the update"
        )

    def test_update_with_type_change(self):
        result = self.db.update({"age": "thirty"}, Field("name").equals("Alice"))
        self.assertTrue(result, "Update with type change should return True")
        updated_entry = self.db.filter(Field("name").equals("Alice"))[0]
        self.assertEqual(
            updated_entry["age"],
            "thirty",
            "Age field should be updated to string value 'thirty'",
        )

    def test_batch_update_all_entries(self):
        result = self.db.batch({"updated": True}, Query(lambda x: True))
        self.assertEqual(
            result,
            3,
            "Batch update with always-true condition should affect all 3 entries",
        )
        all_entries = self.db.get_all()
        self.assertTrue(
            all(entry.get("updated") for entry in all_entries),
            "All entries should have the 'updated' field set to True",
        )


if __name__ == "__main__":
    unittest.main()
