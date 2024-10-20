# effortless/__init__.py
from .configuration import EffortlessConfig
from .effortless import EffortlessDB, db
from .search import Query, Field

__all__ = ["EffortlessDB", "db", "EffortlessConfig", "Query", "Field"]
