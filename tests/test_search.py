import unittest
from effortless import EffortlessDB, Field, Query
import re
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import time

class TestFilter(unittest.TestCase):
    def setUp(self):
        self.db = EffortlessDB()
        self.db.wipe()
        self.db.add(
            {
                "id": 1,
                "name": "Alice",
                "age": 30,
                "skills": ["Python", "JavaScript"],
                "address": {"city": "New York", "country": "USA"},
            }
        )
        self.db.add(
            {
                "id": 2,
                "name": "Bob",
                "age": 25,
                "skills": ["Java", "C++"],
                "address": {"city": "London", "country": "UK"},
            }
        )
        self.db.add(
            {
                "id": 3,
                "name": "Charlie",
                "age": 35,
                "skills": ["Python", "Ruby"],
                "address": {"city": "San Francisco", "country": "USA"},
            }
        )

    def test_equals(self):
        result = self.db.filter(Field("name").equals("Alice"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result["1"]["name"], "Alice")

    def test_contains_case_sensitive(self):
        result = self.db.filter(Field("skills").contains("Python"))
        self.assertEqual(len(result), 2)
        self.assertIn("1", result)
        self.assertIn("3", result)

    def test_contains_case_insensitive(self):
        result = self.db.filter(
            Field("skills").contains("python", case_sensitive=False)
        )
        self.assertEqual(len(result), 2)
        self.assertIn("1", result)
        self.assertIn("3", result)

    def test_startswith_case_sensitive(self):
        result = self.db.filter(Field("name").startswith("A"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result["1"]["name"], "Alice")

    def test_startswith_case_insensitive(self):
        result = self.db.filter(Field("name").startswith("a", case_sensitive=False))
        self.assertEqual(len(result), 1)
        self.assertEqual(result["1"]["name"], "Alice")

    def test_endswith(self):
        result = self.db.filter(Field("name").endswith("e"))
        self.assertEqual(len(result), 2)
        self.assertIn("1", result)
        self.assertIn("3", result)

    def test_greater_than(self):
        result = self.db.filter(Field("age").greater_than(30))
        self.assertEqual(len(result), 1)
        self.assertEqual(result["3"]["name"], "Charlie")

    def test_less_than(self):
        result = self.db.filter(Field("age").less_than(30))
        self.assertEqual(len(result), 1)
        self.assertEqual(result["2"]["name"], "Bob")

    def test_and_query(self):
        result = self.db.filter(
            Field("age").greater_than(25) & Field("skills").contains("Python")
        )
        self.assertEqual(len(result), 2)
        self.assertIn("1", result)
        self.assertIn("3", result)

    def test_or_query(self):
        result = self.db.filter(
            Field("age").less_than(26) | Field("name").equals("Charlie")
        )
        self.assertEqual(len(result), 2)
        self.assertIn("2", result)
        self.assertIn("3", result)

    def test_nested_field(self):
        result = self.db.filter(Field("address.country").equals("USA"))
        self.assertEqual(len(result), 2)
        self.assertIn("1", result)
        self.assertIn("3", result)

    def test_complex_query(self):
        result = self.db.filter(
            (Field("age").greater_than(25) & Field("address.country").equals("USA"))
            | (
                Field("skills").contains("Java")
                & Field("address.city").equals("London")
            )
        )
        self.assertEqual(len(result), 3)
        self.assertIn("1", result)
        self.assertIn("2", result)
        self.assertIn("3", result)

    def test_lambda_query(self):
        result = self.db.filter(
            Query(lambda item: len(item["skills"]) > 1 and item["age"] < 35)
        )
        self.assertEqual(len(result), 2)
        self.assertIn("1", result)
        self.assertIn("2", result)

    def test_empty_result(self):
        result = self.db.filter(Field("name").equals("David"))
        self.assertEqual(len(result), 0)

    def test_invalid_field(self):
        result = self.db.filter(Field("invalid_field").equals("value"))
        self.assertEqual(len(result), 0)

    def test_invalid_nested_field(self):
        result = self.db.filter(Field("address.invalid_field").equals("value"))
        self.assertEqual(len(result), 0)

    def test_multiple_conditions(self):
        result = self.db.filter(
            Field("age").greater_than(25)
            & Field("skills").contains("Python")
            & Field("address.country").equals("USA")
        )
        self.assertEqual(len(result), 2)
        self.assertIn("1", result)
        self.assertIn("3", result)

    def test_complex_nested_query(self):
        query = (Field("age").greater_than(25) & Field("skills").contains("Python")) | (Field("name").startswith("B"))
        result = self.db.filter(query)
        self.assertEqual(len(result), 3)
        self.assertIn("1", result)
        self.assertIn("2", result)
        self.assertIn("3", result)

    def test_nested_field_query(self):
        self.db.wipe()
        self.db.add({"user": {"name": "Alice", "age": 30}})
        self.db.add({"user": {"name": "Bob", "age": 25}})
        
        result = self.db.filter(Field("user.name").equals("Alice"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result["1"]["user"]["name"], "Alice")
        
        result = self.db.filter(Field("user.age").less_than(28))
        self.assertEqual(len(result), 1)
        self.assertEqual(result["2"]["user"]["name"], "Bob")


class TestAdvancedSearch(unittest.TestCase):
    def setUp(self):
        self.db = EffortlessDB()
        self.db.wipe()
        self.db.add({
            "id": 1,
            "name": "Alice Smith",
            "email": "alice@example.com",
            "age": 30,
            "registration_date": "2023-01-15",
            "skills": ["Python", "JavaScript"],
        })
        self.db.add({
            "id": 2,
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "age": 25,
            "registration_date": "2023-02-20",
            "skills": ["Java", "C++"],
        })
        self.db.add({
            "id": 3,
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "age": 35,
            "registration_date": "2023-03-10",
            "skills": ["Python", "Ruby"],
        })

    def test_matches_regex(self):
        # Test email pattern
        result = self.db.filter(Field("email").matches_regex(r"^[a-z]+@example\.com$"))
        self.assertEqual(len(result), 3)

        # Test name pattern
        result = self.db.filter(Field("name").matches_regex(r"^[A-Z][a-z]+ [A-Z][a-z]+$"))
        self.assertEqual(len(result), 3)

        # Test with flags
        result = self.db.filter(Field("name").matches_regex(r"^alice", flags=re.IGNORECASE))
        self.assertEqual(len(result), 1)
        self.assertEqual(result["1"]["name"], "Alice Smith")

    def test_between_dates(self):
        start_date = datetime(2023, 2, 1)
        end_date = datetime(2023, 3, 1)
        
        result = self.db.filter(Field("registration_date").between_dates(start_date, end_date))
        self.assertEqual(len(result), 1)
        self.assertEqual(result["2"]["name"], "Bob Johnson")

        # Test inclusive range
        end_date = datetime(2023, 3, 10)
        result = self.db.filter(Field("registration_date").between_dates(start_date, end_date))
        self.assertEqual(len(result), 2)

    def test_fuzzy_match(self):
        # Exact match
        result = self.db.filter(Field("name").fuzzy_match("Alice Smith"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result["1"]["name"], "Alice Smith")

        # Close match
        result = self.db.filter(Field("name").fuzzy_match("Alice Smth", threshold=0.8))
        self.assertEqual(len(result), 1)
        self.assertEqual(result["1"]["name"], "Alice Smith")

        # No match
        result = self.db.filter(Field("name").fuzzy_match("David", threshold=0.8))
        self.assertEqual(len(result), 0)

    def test_combined_advanced_queries(self):
        # Combine regex and date range
        start_date = datetime(2023, 2, 1)
        end_date = datetime(2023, 12, 31)
        result = self.db.filter(
            Field("email").matches_regex(r"^[bc].*@example\.com$") &
            Field("registration_date").between_dates(start_date, end_date)
        )
        self.assertEqual(len(result), 2)
        self.assertIn("2", result)
        self.assertIn("3", result)

        # Combine fuzzy match and age range
        result = self.db.filter(
            Field("name").fuzzy_match("Charlie", threshold=0.7) &
            Field("age").greater_than(30)
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result["3"]["name"], "Charlie Brown")

    def test_edge_cases(self):
        # Test regex with no matches
        result = self.db.filter(Field("email").matches_regex(r"^[0-9]+@example\.com$"))
        self.assertEqual(len(result), 0)

        # Test date range with no matches
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        result = self.db.filter(Field("registration_date").between_dates(start_date, end_date))
        self.assertEqual(len(result), 0)

        # Test fuzzy match with very low threshold
        result = self.db.filter(Field("name").fuzzy_match("Completely Different", threshold=0.1))
        self.assertEqual(len(result), 3)  # Should match all due to very low threshold

    def test_performance(self):
        # Add a large number of items to test performance
        for i in range(1000):
            self.db.add({
                "id": i + 4,
                "name": f"Test User {i}",
                "email": f"user{i}@example.com",
                "age": 20 + (i % 60),
                "registration_date": (datetime(2023, 1, 1) + timedelta(days=i)).isoformat(),
                "skills": ["Python"] if i % 2 == 0 else ["Java"],
            })

        # Test regex performance
        start_time = time.time()
        result = self.db.filter(Field("email").matches_regex(r"^user[0-9]+@example\.com$"))
        end_time = time.time()
        self.assertEqual(len(result), 1000)
        self.assertLess(end_time - start_time, 1.0)  # Assert that it takes less than 1 second

        # Test date range performance
        start_date = datetime(2023, 6, 1)
        end_date = datetime(2023, 12, 31)
        start_time = time.time()
        result = self.db.filter(Field("registration_date").between_dates(start_date, end_date))
        end_time = time.time()
        self.assertGreater(len(result), 0)
        self.assertLess(end_time - start_time, 1.0)  # Assert that it takes less than 1 second

class TestAdvancedSearchErrors(unittest.TestCase):
    def setUp(self):
        self.db = EffortlessDB()
        self.db.wipe()
        self.db.add({
            "id": 1,
            "name": "Alice Smith",
            "email": "alice@example.com",
            "age": 30,
            "registration_date": "2023-01-15",
            "skills": ["Python", "JavaScript"],
        })

    def test_between_dates_type_error(self):
        # Test with non-datetime objects
        with self.assertRaises(TypeError):
            self.db.filter(Field("registration_date").between_dates("2023-01-01", "2023-12-31"))

        # Test with mixed types
        with self.assertRaises(TypeError):
            self.db.filter(Field("registration_date").between_dates(datetime(2023, 1, 1), "2023-12-31"))

    def test_between_dates_value_error(self):
        # Test with end date before start date
        with self.assertRaises(ValueError):
            self.db.filter(Field("registration_date").between_dates(
                datetime(2023, 12, 31), datetime(2023, 1, 1)
            ))

    def test_matches_regex_type_error(self):
        # Test with non-string pattern
        with self.assertRaises(TypeError):
            self.db.filter(Field("email").matches_regex(123))

    def test_matches_regex_value_error(self):
        # Test with invalid regex pattern
        with self.assertRaises(ValueError):
            self.db.filter(Field("email").matches_regex("["))

    def test_fuzzy_match_type_error(self):
        # Test with non-string value
        with self.assertRaises(TypeError):
            self.db.filter(Field("name").fuzzy_match(123))

        # Test with non-numeric threshold
        with self.assertRaises(ValueError):
            self.db.filter(Field("name").fuzzy_match("Alice", threshold="high"))

    def test_fuzzy_match_value_error(self):
        # Test with threshold out of range
        with self.assertRaises(ValueError):
            self.db.filter(Field("name").fuzzy_match("Alice", threshold=1.5))

        with self.assertRaises(ValueError):
            self.db.filter(Field("name").fuzzy_match("Alice", threshold=-0.1))

    def test_invalid_field_type(self):
        # Test with a field that doesn't exist
        result = self.db.filter(Field("non_existent_field").matches_regex(r".*"))
        self.assertEqual(len(result), 0)

        # Test with a field that isn't a string
        result = self.db.filter(Field("age").matches_regex(r"\d+"))
        self.assertEqual(len(result), 0)

    def test_empty_database(self):
        self.db.wipe()
        result = self.db.filter(Field("name").fuzzy_match("Alice"))
        self.assertEqual(len(result), 0)

    def test_nested_field_errors(self):
        self.db.add({
            "id": 2,
            "name": "Bob Johnson",
            "address": {"city": "New York", "country": "USA"}
        })

        # Test with non-existent nested field
        result = self.db.filter(Field("address.state").equals("NY"))
        self.assertEqual(len(result), 0)

        # Test with partially correct nested field
        result = self.db.filter(Field("address.city.name").equals("New York"))
        self.assertEqual(len(result), 0)

    def test_combined_query_type_mismatch(self):
        # Combining queries with different field types
        result = self.db.filter(
            Field("age").greater_than(25) & Field("name").matches_regex(r"^A")
        )
        self.assertEqual(len(result), 1)  # Should still work, matching Alice

        result = self.db.filter(
            Field("age").greater_than(25) & Field("name").fuzzy_match("Charlie")
        )
        self.assertEqual(len(result), 0)  # No matches due to fuzzy match

    def test_performance_with_invalid_queries(self):
        # Add a large number of items
        for i in range(1000):
            self.db.add({
                "id": i + 2,
                "name": f"Test User {i}",
                "email": f"user{i}@example.com",
                "age": 20 + (i % 60),
                "registration_date": (datetime(2023, 1, 1) + timedelta(days=i)).isoformat(),
            })

        # Test performance with an invalid regex
        start_time = time.time()
        with self.assertRaises(ValueError):
            self.db.filter(Field("email").matches_regex(r"["))
        end_time = time.time()
        self.assertLess(end_time - start_time, 1.0)  # Should fail quickly

        # Test performance with an invalid date range
        start_time = time.time()
        with self.assertRaises(ValueError):
            self.db.filter(Field("registration_date").between_dates(
                datetime(2023, 12, 31), datetime(2023, 1, 1)
            ))
        end_time = time.time()
        self.assertLess(end_time - start_time, 1.0)  # Should fail quickly

if __name__ == "__main__":
    unittest.main()
