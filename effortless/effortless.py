# effortlessdb/effortless.py
import json
import os
import logging
from typing import Any, Dict, List, Optional
import zlib
import base64
import threading
import shutil

logger = logging.getLogger(__name__)


class EffortlessConfig:
    def __init__(self, config: Dict[str, Any] = {}):
        self.debug: bool = config.get("dbg", False)
        self.requires: List[str] = config.get("rq", [])
        self.max_size: Optional[int] = config.get("ms")
        self.v: int = 1
        self.backup: Optional[str] = config.get("bp")
        self.backup_interval: int = config.get("bpi", 1)
        self.encrypted: bool = config.get("enc", False)
        self.compressed: bool = config.get("cmp", False)
        self.readonly: bool = config.get("ro", False)

        self._validate()

    def _validate(self) -> None:
        """Validate the configuration values."""
        if self.max_size is not None and self.max_size <= 0:
            raise ValueError("max_size must be a positive integer")
        if self.v <= 0:
            raise ValueError("Version must be a positive integer")
        if self.backup_interval <= 0:
            raise ValueError("Backup interval must be a positive integer")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dbg": self.debug,
            "rq": self.requires,
            "ms": self.max_size,
            "v": self.v,
            "bp": self.backup,
            "bpi": self.backup_interval,
            "enc": self.encrypted,
            "cmp": self.compressed,
            "ro": self.readonly,
        }

    @staticmethod
    def default_headers():
        return {"headers": EffortlessConfig().to_dict()}


class EffortlessDB:
    def __init__(self, db_name: str = "db"):
        self.config = EffortlessConfig()
        self.set_storage(db_name)
        self._autoconfigure()
        self._operation_count = 0

    @staticmethod
    def default_db():
        ddb = EffortlessConfig.default_headers()
        ddb["content"] = {}
        return ddb

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

        self._autoconfigure()  # configure EffortlessConfig to the new file's configuration

    def _autoconfigure(self) -> None:
        """Ensures the database has a configuration in the headers."""
        data = self._read_db()
        if "v" not in data["headers"]:
            self.config = EffortlessConfig()
            data["headers"] = self.config.to_dict()
            self._write_db(data)
        self._update_config()

    def _update_config(self):
        self.config = EffortlessConfig(self._read_db()["headers"])

    def configure(self, new_config: EffortlessConfig) -> None:
        """Update the database configuration."""
        if not isinstance(new_config, EffortlessConfig):
            raise TypeError("New configuration must be an EffortlessConfig object")

        data = self._read_db()
        self.config = new_config
        content = data["content"]

        data = {"headers": new_config.to_dict(), "content": content}
        self._write_db(data, write_in_readonly=True)
        self._update_config()

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Return all records in the database, excluding configuration."""
        return self._read_db()["content"]

    def search(self, query: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Search the database for items matching the query."""
        results = {}
        for key, item in self._read_db()["content"].items():
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

        for field in self.config.requires:
            if field not in item:
                raise ValueError(
                    f"Field '{field}' is configured to be required in this database"
                )

        try:
            json.dumps(item)
        except (TypeError, ValueError):
            raise ValueError("Item must be JSON-serializable")

        data = self._read_db()
        new_key = str(max((int(k) for k in data["content"].keys()), default=0) + 1)

        if self.config.max_size:
            current_size = os.path.getsize(self._storage_file) / (
                1024 * 1024
            )  # Size in MB
            new_size = current_size + len(json.dumps(item)) / (1024 * 1024)
            if new_size > self.config.max_size:
                raise ValueError(
                    f"The requested operation would increase the size of the database past the configured max db size ({self.config.max_size} MB)."
                )

        data["content"][new_key] = item
        self._write_db(data)
        self._handle_backup()

    def wipe(self, wipe_readonly: bool = False) -> None:
        """Clear all data from the database."""
        self._write_db(
            {"headers": EffortlessConfig().to_dict(), "content": {}},
            write_in_readonly=wipe_readonly,
        )
        self._update_config()

    def _read_db(self) -> Dict[str, Any]:
        """Read the database file."""
        try:
            if not os.path.exists(self._storage_file):
                return {"headers": EffortlessConfig().to_dict(), "content": {}}

            with open(self._storage_file, "rb") as f:
                data = json.loads(f.read().decode())

            headers = data["headers"]
            content = data["content"]

            if headers.get("enc"):
                content = self._decrypt_data(content)

            if headers.get("cmp"):
                content = self._decompress_data(content)

            return {"headers": headers, "content": content}
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading database: {str(e)}")
            raise

    def _write_db(self, data: Dict[str, Any], write_in_readonly: bool = False) -> None:
        """Write data to the database file."""
        try:
            if self.config.readonly and not write_in_readonly:
                raise ValueError("Database is in read-only mode")

            headers = data["headers"]
            content = data["content"]

            if headers.get("cmp"):
                content = self._compress_data(content)

            if headers.get("enc"):
                content = self._encrypt_data(content)

            final_data = json.dumps(
                {"headers": headers, "content": content}, indent=2
            ).encode()

            with open(self._storage_file, "wb") as f:
                f.write(final_data)

            logger.debug(f"Data written to {self._storage_file}")
        except IOError as e:
            logger.error(f"Error writing to database: {str(e)}")
            raise

    def _handle_backup(self) -> None:
        """Handle database backup based on configuration."""
        self._operation_count += 1
        if self.config.backup and self._operation_count >= self.config.backup_interval:
            self._operation_count = 0
            threading.Thread(target=self._backup).start()

    def _backup(self) -> None:
        """Perform database backup."""
        if self.config.backup:
            try:
                backup_path = os.path.join(
                    self.config.backup, os.path.basename(self._storage_file)
                )
                shutil.copy2(self._storage_file, backup_path)
                logger.debug(f"Database backed up to {backup_path}")
            except IOError as e:
                logger.error(f"Backup failed: {str(e)}")

    def _compress_data(self, data: Dict[str, Any]) -> str:
        """Compress the given data and return as a base64-encoded string."""
        compressed = zlib.compress(json.dumps(data).encode())
        return base64.b64encode(compressed).decode()

    def _decompress_data(self, data: str) -> Dict[str, Any]:
        """Decompress the given base64-encoded string data."""
        compressed = base64.b64decode(data.encode())
        return json.loads(zlib.decompress(compressed).decode())

    def _encrypt_data(self, data: Dict[str, Any]) -> str:
        """Encrypt the given data and return as a base64-encoded string."""
        # TODO: Implement actual encryption
        return base64.b64encode(json.dumps(data).encode()).decode()

    def _decrypt_data(self, data: str) -> Dict[str, Any]:
        """Decrypt the given base64-encoded string data."""
        # TODO: Implement actual decryption
        return json.loads(base64.b64decode(data.encode()).decode())

    def _encrypt_value(self, value: Any) -> Any:
        """Encrypt a single value."""
        # TODO: Implement encryption
        return value

    def _decrypt_value(self, value: Any) -> Any:
        """Decrypt a single value."""
        # TODO: Implement decryption
        return value


db = EffortlessDB()
