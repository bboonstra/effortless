import unittest
from effortless import EffortlessDB, Field, Query
import re
from datetime import datetime, timedelta, timezone
import time
import math


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
        self.assertEqual(
            len(result), 1, "There should be exactly one entry with name 'Alice'"
        )
        self.assertEqual(
            result[0]["name"],
            "Alice",
            "The filtered entry should have the name 'Alice'",
        )

    def test_contains_case_sensitive(self):
        result = self.db.filter(Field("skills").contains("Python"))
        self.assertEqual(
            len(result), 2, "There should be two entries with 'Python' in their skills"
        )
        self.assertTrue(
            any(entry["id"] == 1 for entry in result),
            "Alice (id 1) should be in the result",
        )
        self.assertTrue(
            any(entry["id"] == 3 for entry in result),
            "Charlie (id 3) should be in the result",
        )

    def test_contains_case_insensitive(self):
        result = self.db.filter(
            Field("skills").contains("python", case_sensitive=False)
        )
        self.assertEqual(
            len(result),
            2,
            "There should be two entries with 'python' (case-insensitive) in their skills",
        )
        self.assertTrue(
            any(entry["id"] == 1 for entry in result),
            "Alice (id 1) should be in the result",
        )
        self.assertTrue(
            any(entry["id"] == 3 for entry in result),
            "Charlie (id 3) should be in the result",
        )

    def test_startswith_case_sensitive(self):
        result = self.db.filter(Field("name").startswith("A"))
        self.assertEqual(
            len(result), 1, "There should be one entry with a name starting with 'A'"
        )
        self.assertEqual(
            result[0]["name"], "Alice", "The filtered entry should be 'Alice'"
        )

    def test_startswith_case_insensitive(self):
        result = self.db.filter(Field("name").startswith("a", case_sensitive=False))
        self.assertEqual(
            len(result),
            1,
            "There should be one entry with a name starting with 'a' (case-insensitive)",
        )
        self.assertEqual(
            result[0]["name"], "Alice", "The filtered entry should be 'Alice'"
        )

    def test_endswith(self):
        result = self.db.filter(Field("name").endswith("e"))
        self.assertEqual(
            len(result), 2, "There should be two entries with names ending in 'e'"
        )
        self.assertTrue(
            any(entry["id"] == 1 for entry in result),
            "Alice (id 1) should be in the result",
        )
        self.assertTrue(
            any(entry["id"] == 3 for entry in result),
            "Charlie (id 3) should be in the result",
        )

    def test_greater_than(self):
        result = self.db.filter(Field("age").greater_than(30))
        self.assertEqual(
            len(result), 1, "There should be one entry with age greater than 30"
        )
        self.assertEqual(
            result[0]["name"], "Charlie", "The filtered entry should be 'Charlie'"
        )

    def test_less_than(self):
        result = self.db.filter(Field("age").less_than(30))
        self.assertEqual(
            len(result), 1, "There should be one entry with age less than 30"
        )
        self.assertEqual(result[0]["name"], "Bob", "The filtered entry should be 'Bob'")

    def test_and_query(self):
        result = self.db.filter(
            Field("age").greater_than(25) & Field("skills").contains("Python")
        )
        self.assertEqual(
            len(result),
            2,
            "There should be two entries with age > 25 and 'Python' in skills",
        )
        self.assertTrue(
            any(entry["name"] == "Alice" for entry in result),
            "Alice should be in the result",
        )
        self.assertTrue(
            any(entry["name"] == "Charlie" for entry in result),
            "Charlie should be in the result",
        )

    def test_or_query(self):
        result = self.db.filter(
            Field("age").less_than(26) | Field("name").equals("Charlie")
        )
        self.assertEqual(
            len(result),
            2,
            "There should be two entries with age < 26 or name 'Charlie'",
        )
        self.assertTrue(
            any(entry["name"] == "Bob" for entry in result),
            "Bob should be in the result",
        )
        self.assertTrue(
            any(entry["name"] == "Charlie" for entry in result),
            "Charlie should be in the result",
        )

    def test_nested_field(self):
        result = self.db.filter(Field("address.country").equals("USA"))
        self.assertEqual(
            len(result), 2, "There should be two entries with country 'USA'"
        )
        self.assertTrue(
            any(entry["name"] == "Alice" for entry in result),
            "Alice should be in the result",
        )
        self.assertTrue(
            any(entry["name"] == "Charlie" for entry in result),
            "Charlie should be in the result",
        )

    def test_complex_query(self):
        result = self.db.filter(
            (Field("age").greater_than(25) & Field("address.country").equals("USA"))
            | (
                Field("skills").contains("Java")
                & Field("address.city").equals("London")
            )
        )
        self.assertEqual(
            len(result), 3, "There should be three entries matching the complex query"
        )
        self.assertTrue(
            any(entry["name"] == "Alice" for entry in result),
            "Alice should be in the result",
        )
        self.assertTrue(
            any(entry["name"] == "Bob" for entry in result),
            "Bob should be in the result",
        )
        self.assertTrue(
            any(entry["name"] == "Charlie" for entry in result),
            "Charlie should be in the result",
        )

    def test_lambda_query(self):
        result = self.db.filter(
            Query(lambda entry: len(entry["skills"]) > 1 and entry["age"] < 35)
        )
        self.assertEqual(
            len(result),
            2,
            "There should be two entries with more than 1 skill and age < 35",
        )
        self.assertTrue(
            any(entry["name"] == "Alice" for entry in result),
            "Alice should be in the result",
        )
        self.assertTrue(
            any(entry["name"] == "Bob" for entry in result),
            "Bob should be in the result",
        )

    def test_empty_result(self):
        result = self.db.filter(Field("name").equals("David"))
        self.assertEqual(len(result), 0, "There should be no entries with name 'David'")

    def test_invalid_field(self):
        result = self.db.filter(Field("invalid_field").equals("value"))
        self.assertEqual(
            len(result), 0, "There should be no entries with an 'invalid_field'"
        )

    def test_invalid_nested_field(self):
        result = self.db.filter(Field("address.invalid_field").equals("value"))
        self.assertEqual(
            len(result), 0, "There should be no entries with an 'address.invalid_field'"
        )

    def test_multiple_conditions(self):
        result = self.db.filter(
            Field("age").greater_than(25)
            & Field("skills").contains("Python")
            & Field("address.country").equals("USA")
        )
        self.assertEqual(
            len(result), 2, "There should be two entries matching all three conditions"
        )
        self.assertTrue(
            any(entry["name"] == "Alice" for entry in result),
            "Alice should be in the result",
        )
        self.assertTrue(
            any(entry["name"] == "Charlie" for entry in result),
            "Charlie should be in the result",
        )

    def test_complex_nested_query(self):
        query = (Field("age").greater_than(25) & Field("skills").contains("Python")) | (
            Field("name").startswith("B")
        )
        result = self.db.filter(query)
        self.assertEqual(
            len(result),
            3,
            "There should be three entries matching the complex nested query",
        )
        self.assertTrue(
            any(entry["name"] == "Alice" for entry in result),
            "Alice should be in the result",
        )
        self.assertTrue(
            any(entry["name"] == "Bob" for entry in result),
            "Bob should be in the result",
        )
        self.assertTrue(
            any(entry["name"] == "Charlie" for entry in result),
            "Charlie should be in the result",
        )

    def test_nested_field_query(self):
        self.db.wipe()
        self.db.add({"user": {"name": "Alice", "age": 30}})
        self.db.add({"user": {"name": "Bob", "age": 25}})

        result = self.db.filter(Field("user.name").equals("Alice"))
        self.assertEqual(
            len(result), 1, "There should be one entry with user.name 'Alice'"
        )
        self.assertEqual(
            result[0]["user"]["name"],
            "Alice",
            "The filtered entry should have user.name 'Alice'",
        )

        result = self.db.filter(Field("user.age").less_than(28))
        self.assertEqual(len(result), 1, "There should be one entry with user.age < 28")
        self.assertEqual(
            result[0]["user"]["name"], "Bob", "The filtered entry should be Bob"
        )


class TestAdvancedSearch(unittest.TestCase):
    def setUp(self):
        self.db = EffortlessDB()
        self.db.wipe()
        self.db.add(
            {
                "id": 1,
                "name": "Alice Smith",
                "email": "alice@example.com",
                "age": 30,
                "registration_date": "2023-01-15",
                "skills": ["Python", "JavaScript"],
            }
        )
        self.db.add(
            {
                "id": 2,
                "name": "Bob Johnson",
                "email": "bob@example.com",
                "age": 25,
                "registration_date": "2023-02-20",
                "skills": ["Java", "C++"],
            }
        )
        self.db.add(
            {
                "id": 3,
                "name": "Charlie Brown",
                "email": "charlie@example.com",
                "age": 35,
                "registration_date": "2023-03-10",
                "skills": ["Python", "Ruby"],
            }
        )

    def test_matches_regex(self):
        # Test email pattern
        result = self.db.filter(Field("email").matches_regex(r"^[a-z]+@example\.com$"))
        self.assertEqual(len(result), 3)

        # Test name pattern
        result = self.db.filter(
            Field("name").matches_regex(r"^[A-Z][a-z]+ [A-Z][a-z]+$")
        )
        self.assertEqual(len(result), 3)

        # Test with flags
        result = self.db.filter(
            Field("name").matches_regex(r"^alice", flags=re.IGNORECASE)
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice Smith")

    def test_between_dates(self):
        start_date = datetime(2023, 2, 1)
        end_date = datetime(2023, 3, 1)

        result = self.db.filter(
            Field("registration_date").between_dates(start_date, end_date)
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Bob Johnson")

        # Test inclusive range
        end_date = datetime(2023, 3, 10)
        result = self.db.filter(
            Field("registration_date").between_dates(start_date, end_date)
        )
        self.assertEqual(len(result), 2)

    def test_fuzzy_match(self):
        # Exact match
        result = self.db.filter(Field("name").fuzzy_match("Alice Smith"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice Smith")

        # Close match
        result = self.db.filter(Field("name").fuzzy_match("Alice Smth", threshold=0.8))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice Smith")

        # No match
        result = self.db.filter(Field("name").fuzzy_match("David", threshold=0.8))
        self.assertEqual(len(result), 0)

    def test_combined_advanced_queries(self):
        # Combine regex and date range
        start_date = datetime(2023, 2, 1)
        end_date = datetime(2023, 12, 31)
        result = self.db.filter(
            Field("email").matches_regex(r"^[bc].*@example\.com$")
            & Field("registration_date").between_dates(start_date, end_date)
        )
        self.assertEqual(len(result), 2)
        self.assertTrue(any(entry["name"] == "Bob Johnson" for entry in result))
        self.assertTrue(any(entry["name"] == "Charlie Brown" for entry in result))

        # Combine fuzzy match and age range
        result = self.db.filter(
            Field("name").fuzzy_match("Charlie", threshold=0.7)
            & Field("age").greater_than(30)
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Charlie Brown")

    def test_edge_cases(self):
        # Test regex with no matches
        result = self.db.filter(Field("email").matches_regex(r"^[0-9]+@example\.com$"))
        self.assertEqual(len(result), 0)

        # Test date range with no matches
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        result = self.db.filter(
            Field("registration_date").between_dates(start_date, end_date)
        )
        self.assertEqual(len(result), 0)

        # Test fuzzy match with very low threshold
        result = self.db.filter(
            Field("name").fuzzy_match("Completely Different", threshold=0.1)
        )
        self.assertEqual(len(result), 3)  # Should match all due to very low threshold

    def test_performance(self):
        # Add a large number of entries to test performance
        for i in range(1000):
            self.db.add(
                {
                    "id": i + 4,
                    "name": f"Test User {i}",
                    "email": f"user{i}@example.com",
                    "age": 20 + (i % 60),
                    "registration_date": (
                        datetime(2023, 1, 1) + timedelta(days=i)
                    ).isoformat(),
                    "skills": ["Python"] if i % 2 == 0 else ["Java"],
                }
            )

        # Test regex performance
        start_time = time.time()
        result = self.db.filter(
            Field("email").matches_regex(r"^user[0-9]+@example\.com$")
        )
        end_time = time.time()
        self.assertEqual(len(result), 1000)
        self.assertLess(
            end_time - start_time, 1.0
        )  # Assert that it takes less than 1 second

        # Test date range performance
        start_date = datetime(2023, 6, 1)
        end_date = datetime(2023, 12, 31)
        start_time = time.time()
        result = self.db.filter(
            Field("registration_date").between_dates(start_date, end_date)
        )
        end_time = time.time()
        self.assertGreater(len(result), 0)
        self.assertLess(
            end_time - start_time, 1.0
        )  # Assert that it takes less than 1 second

    def test_between_dates_with_unix_timestamps(self):
        # Add entries with Unix timestamp dates
        now = time.time()
        self.db.add(
            {
                "id": 4,
                "name": "David",
                "registration_date": now - 86400,  # Yesterday
            }
        )
        self.db.add(
            {
                "id": 5,
                "name": "Eve",
                "registration_date": now,  # Now
            }
        )
        self.db.add(
            {
                "id": 6,
                "name": "Frank",
                "registration_date": now + 86400,  # Tomorrow
            }
        )

        # Test with Unix timestamp input
        start_date = now - 43200  # 12 hours ago
        end_date = now + 43200  # 12 hours from now

        result = self.db.filter(
            Field("registration_date").between_dates(start_date, end_date)
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Eve")

        # Test with mixed input types
        result = self.db.filter(
            Field("registration_date").between_dates(
                datetime.fromtimestamp(now - 86400, tz=timezone.utc), now + 43200
            )
        )
        self.assertEqual(len(result), 2)
        self.assertTrue(any(entry["name"] == "David" for entry in result))
        self.assertTrue(any(entry["name"] == "Eve" for entry in result))

    def test_between_dates_with_invalid_unix_timestamps(self):
        # Test with negative Unix timestamp
        with self.assertRaises(ValueError):
            self.db.filter(
                Field("registration_date").between_dates(-1, time.time())
            )

        # Test with Unix timestamp that's too large
        with self.assertRaises(ValueError):
            self.db.filter(
                Field("registration_date").between_dates(2**63, time.time())
            )

        # Test with invalid Unix timestamp (string that's not a valid float)
        with self.assertRaises(ValueError):
            self.db.filter(
                Field("registration_date").between_dates("not a timestamp", time.time())
            )

    def test_between_dates_with_future_unix_timestamps(self):
        far_future = time.time() + 31536000  # Approximately one year from now
        result = self.db.filter(
            Field("registration_date").between_dates(far_future, far_future + 86400)
        )
        self.assertEqual(len(result), 0)  # Should be no matches


class TestAdvancedSearchErrors(unittest.TestCase):
    def setUp(self):
        self.db = EffortlessDB()
        self.db.wipe()
        self.db.add(
            {
                "id": 1,
                "name": "Alice Smith",
                "email": "alice@example.com",
                "age": 30,
                "registration_date": "2023-01-15",
                "skills": ["Python", "JavaScript"],
            }
        )

    def test_between_dates_type_error(self):
        # Test with inconvertible date string
        with self.assertRaises(ValueError):
            self.db.filter(
                Field("registration_date").between_dates("not-a-date", "2023-12-31")
            )

        # Test with convertible date strings (should not raise an exception)
        result = self.db.filter(
            Field("registration_date").between_dates("2023-01-01", "2023-12-31")
        )
        self.assertEqual(len(result), 1)

        # Test with mixed types (datetime and string)
        result = self.db.filter(
            Field("registration_date").between_dates(datetime(2023, 1, 1), "2023-12-31")
        )
        self.assertEqual(len(result), 1)

        # Test with mixed types
        result = self.db.filter(
            Field("registration_date").between_dates(datetime(2023, 1, 1), "2023-12-31")
        )
        self.assertEqual(len(result), 1)

    def test_between_dates_value_error(self):
        # Test with end date before start date
        with self.assertRaises(ValueError):
            self.db.filter(
                Field("registration_date").between_dates(
                    datetime(2023, 12, 31), datetime(2023, 1, 1)
                )
            )

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
            self.db.filter(Field("name").fuzzy_match("Alice", threshold="high"))  # type: ignore

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
        self.db.add(
            {
                "id": 2,
                "name": "Bob Johnson",
                "address": {"city": "New York", "country": "USA"},
            }
        )

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
        # Add a large number of entries
        for i in range(1000):
            self.db.add(
                {
                    "id": i + 2,
                    "name": f"Test User {i}",
                    "email": f"user{i}@example.com",
                    "age": 20 + (i % 60),
                    "registration_date": (
                        datetime(2023, 1, 1) + timedelta(days=i)
                    ).isoformat(),
                }
            )

        # Test performance with an invalid regex
        start_time = time.time()
        with self.assertRaises(ValueError):
            self.db.filter(Field("email").matches_regex(r"["))
        end_time = time.time()
        self.assertLess(end_time - start_time, 1.0)  # Should fail quickly

        # Test performance with an invalid date range
        start_time = time.time()
        with self.assertRaises(ValueError):
            self.db.filter(
                Field("registration_date").between_dates(
                    datetime(2023, 12, 31), datetime(2023, 1, 1)
                )
            )
        end_time = time.time()
        self.assertLess(end_time - start_time, 1.0)  # Should fail quickly


class TestPassesMethod(unittest.TestCase):
    def setUp(self):
        self.db = EffortlessDB()
        self.db.wipe()
        self.db.add(
            {
                "id": 1,
                "name": "Alice",
                "age": 30,
                "height": 165.5,
                "is_active": True,
                "skills": ["Python", "JavaScript"],
                "address": {"city": "New York", "country": "USA"},
            }
        )
        self.db.add(
            {
                "id": 2,
                "name": "Bob",
                "age": 25,
                "height": 180.0,
                "is_active": False,
                "skills": ["Java", "C++"],
                "address": {"city": "London", "country": "UK"},
            }
        )
        self.db.add(
            {
                "id": 3,
                "name": "Charlie",
                "age": 35,
                "height": 170.2,
                "is_active": True,
                "skills": ["Python", "Ruby"],
                "address": {"city": "Paris", "country": "France"},
            }
        )

    def test_passes_simple_function(self):
        result = self.db.filter(Field("age").passes(lambda x: x > 30))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Charlie")

    def test_passes_complex_function(self):
        def complex_check(x):
            return x > 25 and x % 2 == 0

        result = self.db.filter(Field("age").passes(complex_check))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice")

    def test_passes_with_external_variable(self):
        threshold = 28
        result = self.db.filter(Field("age").passes(lambda x: x > threshold))
        self.assertEqual(len(result), 2)
        self.assertTrue(any(entry["name"] == "Alice" for entry in result))
        self.assertTrue(any(entry["name"] == "Charlie" for entry in result))

    def test_passes_with_multiple_fields(self):
        def check_name_and_age(entry):
            return len(entry["name"]) > 3 and entry["age"] < 31

        result = self.db.filter(Query(check_name_and_age))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice")

    def test_passes_with_nested_field(self):
        result = self.db.filter(
            Field("address.city").passes(lambda x: x.startswith("L"))
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Bob")

    def test_passes_with_list_field(self):
        result = self.db.filter(Field("skills").passes(lambda x: "Python" in x))
        self.assertEqual(len(result), 2)
        self.assertTrue(any(entry["name"] == "Alice" for entry in result))
        self.assertTrue(any(entry["name"] == "Charlie" for entry in result))

    def test_passes_with_boolean_field(self):
        result = self.db.filter(Field("is_active").passes(lambda x: x is True))
        self.assertEqual(len(result), 2)
        self.assertTrue(any(entry["name"] == "Alice" for entry in result))
        self.assertTrue(any(entry["name"] == "Charlie" for entry in result))

    def test_passes_with_float_field(self):
        result = self.db.filter(Field("height").passes(lambda x: 165 < x < 175))
        self.assertEqual(len(result), 2)
        self.assertTrue(any(entry["name"] == "Alice" for entry in result))
        self.assertTrue(any(entry["name"] == "Charlie" for entry in result))

    def test_passes_with_math_function(self):
        result = self.db.filter(
            Field("height").passes(lambda x: math.isclose(x, 170, abs_tol=5))
        )
        self.assertEqual(len(result), 2)
        self.assertTrue(any(entry["name"] == "Alice" for entry in result))
        self.assertTrue(any(entry["name"] == "Charlie" for entry in result))

    def test_passes_with_exception_handling(self):
        def risky_function(x):
            return 10 / (x - 30)  # Will raise ZeroDivisionError for x = 30

        with self.assertRaises(ValueError) as context:
            self.db.filter(Field("age").passes(risky_function))

        self.assertTrue(
            "Error checking condition 'risky_function'" in str(context.exception)
        )
        self.assertTrue("division by zero" in str(context.exception))

    def test_passes_with_type_checking(self):
        result = self.db.filter(Field("name").passes(lambda x: isinstance(x, str)))
        self.assertEqual(len(result), 3)

    def test_passes_with_no_matches(self):
        result = self.db.filter(Field("age").passes(lambda x: x > 100))
        self.assertEqual(len(result), 0)

    def test_passes_with_all_matches(self):
        result = self.db.filter(Field("age").passes(lambda x: x > 0))
        self.assertEqual(len(result), 3)

    def test_passes_with_lambda_and_method(self):
        result = self.db.filter(
            Field("name").passes(lambda x: x.lower().startswith("a"))
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice")

    def test_passes_with_combined_queries(self):
        result = self.db.filter(
            Field("age").passes(lambda x: x > 25)
            & Field("skills").passes(lambda x: "Python" in x)
        )
        self.assertEqual(len(result), 2)
        self.assertTrue(any(entry["name"] == "Alice" for entry in result))
        self.assertTrue(any(entry["name"] == "Charlie" for entry in result))

    def test_passes_with_or_combined_queries(self):
        result = self.db.filter(
            Field("age").passes(lambda x: x < 26)
            | Field("height").passes(lambda x: x > 175)
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Bob")

    def test_passes_with_nonexistent_field(self):
        result = self.db.filter(Field("nonexistent").passes(lambda x: x is not None))
        self.assertEqual(len(result), 0)

    def test_passes_with_none_value(self):
        self.db.add({"id": 4, "name": "David", "age": None})
        print("\nDatabase contents:")
        print(self.db.get_all())

        def check_none(x):
            print(f"Checking value: {x}")
            return x is None

        result = self.db.filter(Field("age").passes(check_none))
        print("Filter result:", result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "David")


class TestIsType(unittest.TestCase):
    def setUp(self):
        self.db = EffortlessDB()
        self.db.wipe()
        self.db.add(
            {
                "id": 1,
                "name": "Alice",
                "age": 30,
                "height": 165.5,
                "is_active": True,
                "skills": ["Python", "JavaScript"],
                "address": {"city": "New York", "country": "USA"},
            }
        )
        self.db.add(
            {
                "id": 2,
                "name": "Bob",
                "age": "25",  # String instead of int
                "height": "180.0",  # String instead of float
                "is_active": "true",  # String instead of bool
                "skills": "Java, C++",  # String instead of list
                "address": "London, UK",  # String instead of dict
            }
        )

    def test_is_type(self):
        result = self.db.filter(Field("age").is_type(int))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice")

        result = self.db.filter(Field("height").is_type(float))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice")

        result = self.db.filter(Field("is_active").is_type(bool))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice")

        result = self.db.filter(Field("skills").is_type(list))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice")

        result = self.db.filter(Field("address").is_type(dict))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice")

    def test_is_type_with_string(self):
        result = self.db.filter(Field("age").is_type(str))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Bob")

    def test_is_type_combined_query(self):
        result = self.db.filter(
            Field("age").is_type(int) & Field("height").is_type(float)
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Alice")

    def test_is_type_no_matches(self):
        result = self.db.filter(Field("name").is_type(int))
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
