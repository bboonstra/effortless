# effortlessdb/effortless.py
import json
import os
from typing import Any, Dict


DEFAULT_CONFIGURATION = {"v": 1}


class Effortless:
    def __init__(self, db_name: str = "db"):
        self.set_storage(db_name)
        self._ensure_configuration()

    def set_directory(self, directory: str) -> None:
        """
        Set the directory for the database file.

        Args:
            directory (str): The directory path where the database file will be stored.

        Raises:
            TypeError: If directory is not a string.
            ValueError: If directory is empty or does not exist.
        """
        if not isinstance(directory, str):
            raise TypeError("The database directory must be a string")
        if not directory:
            raise ValueError("The database directory cannot be empty.")
        if not os.path.isdir(directory):
            raise ValueError(f"The database path ({directory}) does not exist.")

        self._storage_directory = directory
        self._update_storage_file()

    def set_storage(self, db_name: str) -> None:
        """
        Set the storage file for the database.

        Args:
            db_name (str): The name of the database file (without extension).
                           This will be used as the prefix for the .effortless file.

        Raises:
            TypeError: If db_name is not a string.
            ValueError: If db_name is empty or contains invalid characters.

        Note:
            The actual file will be named '{db_name}.effortless'.
        """

        if not isinstance(db_name, str):
            raise TypeError("The database name must be a string")
        if not db_name:
            raise ValueError("Database name cannot be empty")
        if not all(c.isalnum() or c in "-_" for c in db_name):
            raise ValueError(
                "Database name must contain only alphanumeric characters, underscores, or dashes"
            )

        self._storage_filename = f"{db_name}.effortless"
        self._update_storage_file()

    def _update_storage_file(self) -> None:
        """
        Update the _storage_file based on the current directory and filename.
        Creates the database file if it doesn't exist.
        """
        if hasattr(self, "_storage_directory"):
            self._storage_file = os.path.join(
                self._storage_directory, self._storage_filename
            )
        else:
            self._storage_file = self._storage_filename

        # Create the database file if it doesn't exist
        if not os.path.exists(self._storage_file):
            self._create_db()

    def _ensure_configuration(self) -> None:
        """Ensure the database has a configuration."""
        data = self._read_db()
        if not data:
            data = {"0": DEFAULT_CONFIGURATION}
        elif "0" not in data or "v" not in data["0"]:
            data["0"] = DEFAULT_CONFIGURATION
        self._write_db(data)

    def configure(self, config: Dict[str, Any]) -> None:
        """Update the database configuration."""
        if not isinstance(config, dict):
            raise TypeError("Configuration must be a dictionary")
        data = self._read_db()
        data["0"].update(config)
        self._write_db(data)

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Return all records in the database, excluding configuration."""
        return self._get_user_data()

    def _get_user_data(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve only user data from the database."""
        data = self._read_db()
        return {key: value for key, value in data.items() if key != "0"}

    def search(self, query: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Search the database for items matching the query."""
        results = {}
        for key, item in self._get_user_data().items():
            if all(self._match_item(item.get(k), v) for k, v in query.items()):
                results[key] = item
        return results

    def _match_item(self, item_value: Any, query_value: Any) -> bool:
        """Check if the item value matches the query value."""
        if isinstance(item_value, list):
            return query_value in item_value
        return item_value == query_value

    def add(self, item: dict) -> None:
        """Add an item to the database."""
        if not isinstance(item, dict):
            raise TypeError("Item must be a dictionary")
        try:
            json.dumps(item)
        except (TypeError, ValueError):
            raise ValueError("Item must be JSON-serializable")

        data = self._read_db()
        new_key = str(max((int(k) for k in data.keys() if k != "0"), default=0) + 1)
        data[new_key] = item
        self._write_db(data)

    def wipe(self) -> None:
        """Clear all data from the database."""
        self._write_db({"0": DEFAULT_CONFIGURATION})

    def _read_db(self) -> Dict[str, Any]:
        """Read the database file."""
        if not os.path.exists(self._storage_file):
            self._create_db()
        with open(self._storage_file, "r") as f:
            return json.load(f)

    def _write_db(self, data: Dict[str, Any]) -> None:
        """Write data to the database file."""
        if not os.path.exists(self._storage_file):
            self._create_db()
        with open(self._storage_file, "w") as f:
            json.dump(data, f, indent=2)

    def _create_db(self) -> None:
        """Create a new database file with default configuration."""
        initial_data = {"0": DEFAULT_CONFIGURATION}
        
        with open(self._storage_file, "w") as f:
            json.dump(initial_data, f, indent=2)


db = Effortless()
