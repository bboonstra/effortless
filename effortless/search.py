from abc import ABC, abstractmethod
from typing import Callable, Union, Tuple, List, Type
import re
from datetime import datetime
from difflib import SequenceMatcher


class BaseQuery(ABC):
    """
    Abstract base class for all query types.

    This class defines the basic structure and operations for queries.
    """

    @abstractmethod
    def match(self, item):
        """
        Abstract method to check if an item matches the query.

        Args:
            item: The item to check against the query.

        Returns:
            bool: True if the item matches the query, False otherwise.
        """
        pass

    def __and__(self, other):
        """
        Combine this query with another using AND logic.

        Args:
            other (BaseQuery): Another query to combine with this one.

        Returns:
            AndQuery: A new query representing the AND combination.
        """
        return AndQuery(self, other)

    def __or__(self, other):
        """
        Combine this query with another using OR logic.

        Args:
            other (BaseQuery): Another query to combine with this one.

        Returns:
            OrQuery: A new query representing the OR combination.
        """
        return OrQuery(self, other)


class Query(BaseQuery):
    """
    Main query class that supports various filtering operations.

    This class can be initialized with either a callable condition or a field name.
    It provides methods for different types of comparisons and matching.
    """

    def __init__(
        self,
        condition_or_field: Union[
            Callable[[dict], bool], str, Tuple[str, ...], List[str]
        ],
    ):
        """
        Initialize a Query object.

        Args:
            condition_or_field: Either a callable that takes a dict and returns a bool,
                                or a string (or tuple/list of strings) representing a field name.
        """
        if callable(condition_or_field):
            self.condition = condition_or_field
            self.field = None
        else:
            self.field = condition_or_field
            self.condition = None

    def __and__(self, other):
        """
        Combine this query with another using AND logic.

        Args:
            other (Query): Another query to combine with this one.

        Returns:
            CombinedQuery: A new query representing the AND combination.
        """
        return CombinedQuery(self, other, lambda a, b: a and b)

    def __or__(self, other):
        """
        Combine this query with another using OR logic.

        Args:
            other (Query): Another query to combine with this one.

        Returns:
            CombinedQuery: A new query representing the OR combination.
        """
        return CombinedQuery(self, other, lambda a, b: a or b)

    def match(self, item):
        """
        Check if an item matches this query.

        Args:
            item (dict): The item to check against the query.

        Returns:
            bool: True if the item matches the query, False otherwise.
        """
        if self.condition:
            return self.condition(item)
        return True  # Default to True if no condition is set

    def _validate_field(self, item):
        """
        Check if the field exists in the item.

        Args:
            item (dict): The item to check.

        Returns:
            bool: True if the field exists, False otherwise.
        """
        try:
            self._get_nested_value(item, self.field)
            return True
        except KeyError:
            return False

    def _get_nested_value(self, item, field):
        """
        Get the value of a potentially nested field in an item.

        Args:
            item (dict): The item to search in.
            field (str): The field name, potentially with dot notation for nested fields.

        Returns:
            The value of the field, or None if not found.
        """
        keys = field.split(".")
        value = item
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    def equals(self, value):
        """
        Create a condition that checks if the field equals the given value.

        Args:
            value: The value to compare against.

        Returns:
            Query: This query object with the new condition.
        """
        self.condition = (
            lambda item: self._validate_field(item)
            and self._get_nested_value(item, self.field) == value
        )
        return self

    def contains(self, value, case_sensitive=True):
        """
        Create a condition that checks if the field contains the given value.

        Args:
            value: The value to search for.
            case_sensitive (bool): Whether the search should be case-sensitive.

        Returns:
            Query: This query object with the new condition.
        """

        def condition(item):
            field_value = self._get_nested_value(item, self.field)
            if isinstance(field_value, str):
                return (
                    value.lower() in field_value.lower()
                    if not case_sensitive
                    else value in field_value
                )
            elif isinstance(field_value, list):
                if case_sensitive:
                    return value in field_value
                else:
                    return any(
                        value.lower() == item.lower()
                        for item in field_value
                        if isinstance(item, str)
                    )
            return False

        self.condition = lambda item: self._validate_field(item) and condition(item)
        return self

    def startswith(self, value, case_sensitive=True):
        """
        Create a condition that checks if the field starts with the given value.

        Args:
            value (str): The value to check for at the start of the field.
            case_sensitive (bool): Whether the check should be case-sensitive.

        Returns:
            Query: This query object with the new condition.
        """

        def condition(item):
            field_value = str(self._get_nested_value(item, self.field))
            if not case_sensitive:
                return field_value.lower().startswith(value.lower())
            return field_value.startswith(value)

        self.condition = lambda item: self._validate_field(item) and condition(item)
        return self

    def endswith(self, value):
        """
        Create a condition that checks if the field ends with the given value.

        Args:
            value (str): The value to check for at the end of the field.

        Returns:
            Query: This query object with the new condition.
        """
        self.condition = lambda item: self._validate_field(item) and str(
            self._get_nested_value(item, self.field)
        ).endswith(value)
        return self

    def greater_than(self, value):
        """
        Create a condition that checks if the field is greater than the given value.

        Args:
            value: The value to compare against.

        Returns:
            Query: This query object with the new condition.
        """
        self.condition = (
            lambda item: self._validate_field(item)
            and self._get_nested_value(item, self.field) > value
        )
        return self

    def less_than(self, value):
        """
        Create a condition that checks if the field is less than the given value.

        Args:
            value: The value to compare against.

        Returns:
            Query: This query object with the new condition.
        """
        self.condition = (
            lambda item: self._validate_field(item)
            and self._get_nested_value(item, self.field) < value
        )
        return self

    def matches_regex(self, pattern, flags=0):
        """
        Create a condition that checks if the field matches the given regex pattern.

        Args:
            pattern (str): The regex pattern to match against.
            flags (int): Regex flags to use.

        Returns:
            Query: This query object with the new condition.

        Raises:
            TypeError: If the pattern is not a string.
            ValueError: If the regex pattern is invalid.
        """
        if not isinstance(pattern, str):
            raise TypeError("Regex pattern must be a string")
        try:
            compiled_pattern = re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

        def condition(item):
            field_value = self._get_nested_value(item, self.field)
            if not isinstance(field_value, str):
                return False  # Return False for non-string fields
            return compiled_pattern.search(field_value) is not None

        self.condition = lambda item: self._validate_field(item) and condition(item)
        return self

    def between_dates(self, start_date, end_date):
        """
        Create a condition that checks if the field's date is between the given dates.

        Args:
            start_date (datetime): The start date of the range.
            end_date (datetime): The end date of the range.

        Returns:
            Query: This query object with the new condition.

        Raises:
            TypeError: If start_date or end_date is not a datetime object.
            ValueError: If start_date is after end_date.
        """
        def to_datetime(date):
            if isinstance(date, str):
                try:
                    return datetime.fromisoformat(date)
                except ValueError:
                    raise ValueError(f"Invalid date format: {date}")
            elif isinstance(date, datetime):
                return date
            else:
                raise TypeError(f"Date must be a string or datetime object, not {type(date)}")

        start_date = to_datetime(start_date)
        end_date = to_datetime(end_date)
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")

        def condition(item):
            field_value = self._get_nested_value(item, self.field)
            if isinstance(field_value, str):
                try:
                    field_value = datetime.fromisoformat(field_value)
                except ValueError:
                    return False
            return start_date <= field_value <= end_date

        self.condition = lambda item: self._validate_field(item) and condition(item)
        return self

    def fuzzy_match(self, value, threshold=0.8):
        """
        Create a condition that checks if the field fuzzy matches the given value.

        Args:
            value (str): The value to fuzzy match against.
            threshold (float): The similarity threshold (0 to 1) for a match.

        Returns:
            Query: This query object with the new condition.

        Raises:
            TypeError: If value is not a string.
            ValueError: If threshold is not between 0 and 1.
        """
        if not isinstance(value, str):
            raise TypeError("Fuzzy match value must be a string")
        if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
            raise ValueError("Threshold must be a number between 0 and 1")

        def condition(item):
            field_value = str(self._get_nested_value(item, self.field))
            return SequenceMatcher(None, field_value, value).ratio() >= threshold

        self.condition = lambda item: self._validate_field(item) and condition(item)
        return self

    def passes(self, func):
        """
        Create a condition that checks if the field passes the given function.

        Args:
            func (callable): A function that takes the field value and returns a boolean.

        Returns:
            Query: This query object with the new condition.
        """

        def condition(item):
            field_value = self._get_nested_value(item, self.field)
            try:
                return func(field_value)
            except Exception as e:
                func_name = getattr(func, "__name__", "unnamed function")
                raise ValueError(
                    f"Error checking condition '{func_name}': {str(e)}"
                ) from e

        self.condition = lambda item: self._validate_field(item) and condition(item)
        return self

    def is_type(self, expected_type: Type):
        """
        Create a condition that checks if the field is of the expected type.

        Args:
            expected_type (Type): The expected type of the field.

        Returns:
            Query: This query object with the new condition.
        """

        def condition(item):
            field_value = self._get_nested_value(item, self.field)
            return isinstance(field_value, expected_type)

        self.condition = lambda item: self._validate_field(item) and condition(item)
        return self


class AndQuery(BaseQuery):
    """
    A query that combines multiple queries with AND logic.
    """

    def __init__(self, *queries):
        """
        Initialize an AndQuery with multiple queries.

        Args:
            *queries: Variable number of Query objects to combine with AND logic.
        """
        self.queries = queries

    def match(self, item):
        """
        Check if an item matches all the combined queries.

        Args:
            item: The item to check against the queries.

        Returns:
            bool: True if the item matches all queries, False otherwise.
        """
        return all(query.match(item) for query in self.queries)


class OrQuery(BaseQuery):
    """
    A query that combines multiple queries with OR logic.
    """

    def __init__(self, *queries):
        """
        Initialize an OrQuery with multiple queries.

        Args:
            *queries: Variable number of Query objects to combine with OR logic.
        """
        self.queries = queries

    def match(self, item):
        """
        Check if an item matches any of the combined queries.

        Args:
            item: The item to check against the queries.

        Returns:
            bool: True if the item matches any query, False otherwise.
        """
        return any(query.match(item) for query in self.queries)


class CombinedQuery(Query):
    """
    A query that combines two queries with a custom combination function.
    """

    def __init__(self, query1, query2, combine_func):
        """
        Initialize a CombinedQuery with two queries and a combination function.

        Args:
            query1 (Query): The first query to combine.
            query2 (Query): The second query to combine.
            combine_func (callable): A function that takes two boolean arguments and returns a boolean.
        """
        self.query1 = query1
        self.query2 = query2
        self.combine_func = combine_func

    def match(self, item):
        """
        Check if an item matches the combined query.

        Args:
            item: The item to check against the combined query.

        Returns:
            bool: The result of applying the combination function to the results of both queries.
        """
        return self.combine_func(self.query1.match(item), self.query2.match(item))


def Field(field_name: str) -> Query:
    """
    Create a new Query object for the specified field.

    Args:
        field_name (str): The name of the field to query.

    Returns:
        Query: A new Query object for the specified field.
    """
    return Query(field_name)


class FieldNotFoundError(Exception):
    """
    Exception raised when a specified field is not found in an item.
    """

    pass
