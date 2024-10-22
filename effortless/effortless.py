# effortlessdb/effortless.py
import json
import os
import logging
from typing import Any, Dict, List, Union
import zlib
import base64
import threading
import shutil
from effortless.configuration import EffortlessConfig
from effortless.search import Query

logger = logging.getLogger(__name__)


class EffortlessDB:
    def __init__(self, db_name: str = "db"):
        """
        Initialize an EffortlessDB instance.

        This constructor sets up a new database with the given name. If no name is provided,
        it defaults to "db". It sets up the storage and performs initial auto-configuration.

        Args:
            db_name (str, optional): The name of the database. Defaults to "db".

        """
        self.config = EffortlessConfig()
        self.set_storage(db_name)
        self._autoconfigure()
        self._operation_count = 0
        self._backup_thread = None

    @staticmethod
    def default_db():
        """
        Create and return a default database structure.

        This method generates a dictionary representing an empty database with default headers.
        This is mainly used for test cases and you probably don't need it.

        Returns:
            dict: A dictionary with 'headers' (default configuration) and an empty 'content'.
        """
        ddb = EffortlessConfig.default_headers()
        ddb["content"] = []  # Changed to an empty list
        return ddb

    def set_directory(self, directory: str) -> None:
        """
        Set the directory for the database file.

        This method specifies where the database file should be stored. It updates the
        internal storage path and triggers a reconfiguration of the database.

        Args:
            directory (str): The directory path where the database file will be stored. Use set_storage to set the filename.

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

        This method determines the filename for the database storage. It appends
        the '.effortless' extension to the provided name and updates the storage configuration.

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

        This internal method combines the storage directory (if set) with the filename
        to create the full path for the database file. It then triggers an auto-configuration
        to ensure the database is properly set up for the new location.

        Note:
            This method is called internally when the storage location changes.
        """
        if hasattr(self, "_storage_directory"):
            self._storage_file = os.path.join(
                self._storage_directory, self._storage_filename
            )
        else:
            self._storage_file = self._storage_filename

        self._autoconfigure()  # configure EffortlessConfig to the new file's configuration

    def _autoconfigure(self) -> None:
        """
        Ensure the database has a valid configuration in its headers.

        This method checks if the database file has a valid configuration. If not,
        it creates a default configuration and writes it to the file. It then
        updates the internal configuration object to match the file's configuration.

        Note:
            This method is called internally during initialization and when the storage changes.
        """
        data = self._read_db()
        if "v" not in data["headers"]:
            self.config = EffortlessConfig()
            data["headers"] = self.config.to_dict()
            self._write_db(data)
        self._update_config()

    def _update_config(self):
        """
        Update the internal configuration object based on the database file.

        This method reads the configuration from the database file and updates
        the internal config object accordingly. It ensures that the in-memory
        configuration always matches the one stored in the file.

        Note:
            This method is called internally after operations that might change the configuration.
        """
        self.config = EffortlessConfig(self._read_db()["headers"])

    def configure(self, new_config: EffortlessConfig) -> None:
        """
        Update the database configuration.

        This method allows you to change the configuration of the database. It updates
        both the in-memory configuration and the configuration stored in the file.

        Args:
            new_config (EffortlessConfig): The new configuration object to apply.

        Raises:
            TypeError: If new_config is not an EffortlessConfig object.

        Note:
            This method will write to the database file even if it's in read-only mode; read-only mode only protects against edits to the database's content.
        """
        if not isinstance(new_config, EffortlessConfig):
            raise TypeError("New configuration must be an EffortlessConfig object")

        data = self._read_db()
        self.config = new_config
        content = data["content"]

        data = {"headers": new_config.to_dict(), "content": content}
        self._write_db(data, write_in_readonly=True)
        self._update_config()

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Retrieve all records from the database.

        This method returns all the data stored in the database, excluding the configuration.
        The returned list contains all records in the database.

        Returns:
            List[Dict[str, Any]]: A list where each entry is a record in the database.
        """
        return self._read_db()["content"]

    def filter(self, query: Query) -> List[Dict[str, Any]]:
        """
        Filter the database records based on a given query.

        This method applies the provided query to all records in the database and returns
        the matching results.

        Args:
            query (Query): A Query object defining the filter criteria.

        Returns:
            List[Dict[str, Any]]: A list of records that match the query criteria.
        """
        return [entry for entry in self.get_all() if query.match(entry)]

    def add(self, entry: dict) -> None:
        """
        Add a new entry to the database.

        This method adds a new record to the database. It performs several checks:
        - Ensures the entry is a dictionary
        - Verifies that all required fields (as per configuration) are present
        - Checks if the entry is JSON-serializable
        - Verifies that adding the entry won't exceed the configured max size (if set)

        Args:
            entry (dict): The entry to be added to the database.

        Raises:
            TypeError: If the entry is not a dictionary.
            ValueError: If a required field is missing, if the entry is not JSON-serializable,
                        or if adding the entry would exceed the max size limit.

        Note:
            This method also triggers a backup if the backup conditions are met.
        """
        if not isinstance(entry, dict):
            raise TypeError("Entry must be a dictionary")

        for field in self.config.requires:
            if field not in entry:
                raise ValueError(
                    f"Field '{field}' is configured to be required in this database"
                )

        try:
            json.dumps(entry)
        except (TypeError, ValueError):
            raise ValueError("Entry must be JSON-serializable")

        data = self._read_db()

        if self.config.max_size:
            current_size = os.path.getsize(self._storage_file) / (
                1024 * 1024
            )  # Size in MB
            new_size = current_size + len(json.dumps(entry)) / (1024 * 1024)
            if new_size > self.config.max_size:
                raise ValueError(
                    f"The requested operation would increase the size of the database past the configured max db size ({self.config.max_size} MB)."
                )

        data["content"].append(entry)
        self._write_db(data)
        self._handle_backup()

    def wipe(self, wipe_readonly: bool = False) -> None:
        """
        Clear all data from the database.

        This method removes all content and headers from the database, resetting it to its initial state.

        Args:
            wipe_readonly (bool, optional): If True, allows wiping even if the database is in read-only mode.
                                            Defaults to False.

        Note:
            Use this method with caution as it permanently deletes all data in the database. This will not wipe backups.
        """
        self._write_db(
            {"headers": EffortlessConfig().to_dict(), "content": []},
            write_in_readonly=wipe_readonly,
        )
        self._update_config()

    def _read_db(self) -> Dict[str, Any]:
        """
        Read the contents of the database file.

        This internal method reads the database file, handling decryption and decompression
        if these features are enabled in the configuration.

        Returns:
            Dict[str, Any]: A dictionary containing the database headers and content.

        Raises:
            IOError: If there's an error reading the file.
            json.JSONDecodeError: If the file content is not valid JSON.

        Note:
            If the database file doesn't exist, it returns a default empty database structure.
        """
        try:
            if not os.path.exists(self._storage_file):
                return {"headers": EffortlessConfig().to_dict(), "content": []}

            with open(self._storage_file, "rb") as f:
                data = json.loads(f.read().decode())

            headers = data["headers"]
            content = data["content"]

            if headers.get("cmp"):
                content = self._decompress_data(content)

            if headers.get("enc"):
                content = self._decrypt_data(content if isinstance(content, str) else json.dumps(content))

            return {"headers": headers, "content": content}
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading database: {str(e)}")
            raise

    def _write_db(self, data: Dict[str, Any], write_in_readonly: bool = False) -> None:
        """
        Write data to the database file.

        This internal method writes the provided data to the database file, handling
        compression and encryption if these features are enabled in the configuration.

        Args:
            data (Dict[str, Any]): The data to write to the database.
            write_in_readonly (bool, optional): If True, allows writing even if the database
                                                is in read-only mode. Defaults to False.

        Raises:
            ValueError: If attempting to write to a read-only database without permission.
            IOError: If there's an error writing to the file.

        Note:
            This method is used internally for all database write operations.
        """
        try:
            if self.config.readonly and not write_in_readonly:
                raise ValueError("Database is in read-only mode")

            headers = data["headers"]
            content = data["content"]
            
            if headers.get("enc"):
                content = self._encrypt_data(content)
            
            if headers.get("cmp"):
                content = self._compress_data(json.dumps(content))

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
        """
        Handle database backup based on configuration.

        This method is called after each write operation. It increments an operation counter
        and triggers a backup when the counter reaches the configured backup interval.

        Note:
            Backups are performed in a separate thread to avoid blocking the main operation.
        """
        self._operation_count += 1
        if self.config.backup and self._operation_count >= self.config.backup_interval:
            self._operation_count = 0

            # If a backup thread is already running, we can stop it
            if self._backup_thread and self._backup_thread.is_alive():
                self._backup_thread.join(timeout=0)  # Non-blocking join
                if self._backup_thread.is_alive() and self.config.debug:
                    logger.debug("Previous backup thread is alive and not stopping")

            # Start a new backup thread
            self._backup_thread = threading.Thread(target=self._backup)
            self._backup_thread.start()

    def finish_backup(self, timeout: float | None = None) -> bool:
        """
        Wait for any ongoing backup operation to complete.

        This method blocks until the current backup thread (if any) has finished.

        Args:
            timeout (float, optional): Maximum time to wait for the backup to complete, in seconds.
                                       If None, wait indefinitely. Defaults to None.

        Returns:
            bool: True if the backup completed (or there was no backup running),
                  False if the timeout was reached before the backup completed.
        """
        if self._backup_thread and self._backup_thread.is_alive():
            self._backup_thread.join(timeout)
            return not self._backup_thread.is_alive()
        return True

    def _backup(self) -> bool:
        """
        Perform a database backup.

        This method creates a copy of the database file in the configured backup location.
        It's typically called by _handle_backup() in a separate thread.

        Note:
            If the backup fails, an error is logged but no exception is raised to the caller.
        """
        if self.config.backup:
            try:
                # Check if backup directory is valid
                if not os.path.exists(self.config.backup) or not os.access(
                    self.config.backup, os.W_OK
                ):
                    raise IOError(
                        f"Backup directory {self.config.backup} is not writable or does not exist."
                    )

                backup_path = os.path.join(
                    self.config.backup, os.path.basename(self._storage_file)
                )
                shutil.copy2(self._storage_file, backup_path)
                logger.debug(f"Database backed up to {backup_path}")
                return True  # Indicate success
            except IOError as e:
                logger.error(f"Backup failed: {str(e)}")
                return False  # Indicate failure
            
        return False

    def _compress_data(self, data: Union[str, Dict[str, Any]]) -> str:
        """
        Compress the given data and return as a base64-encoded string.

        Args:
            data (Union[str, Dict[str, Any]]): The data to be compressed.

        Returns:
            str: A base64-encoded string of the compressed data.
        """
        if isinstance(data, dict):
            data = json.dumps(data)
        compressed = zlib.compress(data.encode())
        return base64.b64encode(compressed).decode()

    def _decompress_data(self, data: str) -> Dict[str, Any]:
        """
        Decompress the given base64-encoded string data.

        This method decodes the base64 string, decompresses it using zlib,
        and then parses it as JSON.

        Args:
            data (str): The base64-encoded compressed data.

        Returns:
            Dict[str, Any]: The decompressed and parsed data.
        """
        compressed = base64.b64decode(data.encode())
        return json.loads(zlib.decompress(compressed).decode())

    def _encrypt_data(self, data: Dict[str, Any]) -> str:
        """
        Encrypt the given data and return as a base64-encoded string.

        Note: TODO This is a placeholder method and does not actually perform encryption.
        It should be implemented with proper encryption algorithms in a production environment.

        Args:
            data (Dict[str, Any]): The data to be encrypted.

        Returns:
            str: A base64-encoded string of the "encrypted" data.
        """
        # TODO: Implement actual encryption
        return base64.b64encode(json.dumps(data).encode()).decode()

    def _decrypt_data(self, data: str) -> Dict[str, Any]:
        """
        Decrypt the given base64-encoded string data.

        Note: TODO This is a placeholder method and does not actually perform decryption.
        It should be implemented with proper decryption algorithms in a production environment.

        Args:
            data (str): The base64-encoded "encrypted" data.

        Returns:
            Dict[str, Any]: The "decrypted" and parsed data.
        """
        # TODO: Implement actual decryption
        return json.loads(base64.b64decode(data.encode()).decode())

    def _encrypt_value(self, value: Any) -> Any:
        """
        Encrypt a single value.

        Note: TODO This is a placeholder method and does not actually perform encryption.
        It should be implemented with proper encryption algorithms in a production environment.

        Args:
            value (Any): The value to be encrypted.

        Returns:
            Any: The "encrypted" value (currently unchanged).
        """
        # TODO: Implement encryption
        return value

    def _decrypt_value(self, value: Any) -> Any:
        """
        Decrypt a single value.

        Note: TODO This is a placeholder method and does not actually perform decryption.
        It should be implemented with proper decryption algorithms in a production environment.

        Args:
            value (Any): The value to be decrypted.

        Returns:
            Any: The "decrypted" value (currently unchanged).
        """
        # TODO: Implement decryption
        return value

    def update(self, update_data: Dict[str, Any], condition: Query) -> bool:
        """
        Update a single entry in the database that matches the given condition.

        Args:
            update_data (Dict[str, Any]): The data to update the matching entry with.
            condition (Query): A Query object defining the condition to match.

        Returns:
            bool: True if an entry was updated, False if no matching entry was found.

        Raises:
            ValueError: If more than one entry matches the condition.
        """
        data = self._read_db()
        matching_entries = [
            entry for entry in data["content"] if condition.match(entry)
        ]

        if len(matching_entries) > 1:
            raise ValueError(
                "More than one entry matches the given condition. If you want to update multiple entries at once, use batch() instead."
            )
        elif len(matching_entries) == 0:
            return False

        index = data["content"].index(matching_entries[0])
        data["content"][index].update(update_data)
        self._write_db(data)
        self._handle_backup()
        return True

    def batch(self, update_data: Dict[str, Any], condition: Query) -> int:
        """
        Update all entries in the database that match the given condition.

        Args:
            update_data (Dict[str, Any]): The data to update the matching entries with.
            condition (Query): A Query object defining the condition to match.

        Returns:
            int: The number of entries that were updated.
        """
        data = self._read_db()
        updated_count = 0

        for entry in data["content"]:
            if condition.match(entry):
                entry.update(update_data)
                updated_count += 1

        if updated_count > 0:
            self._write_db(data)
            self._handle_backup()

        return updated_count

    def remove(self, condition: Query) -> bool:
        """
        Remove a single entry from the database that matches the given condition.

        Args:
            condition (Query): A Query object defining the condition to match.

        Returns:
            bool: True if an entry was removed, False if no matching entry was found.

        Raises:
            ValueError: If more than one entry matches the condition.
        """
        data = self._read_db()
        matching_entries = [
            entry for entry in data["content"] if condition.match(entry)
        ]

        if len(matching_entries) > 1:
            raise ValueError(
                "More than one entry matches the given condition. If you want to remove multiple entries at once, use erase() instead."
            )
        elif len(matching_entries) == 0:
            return False

        data["content"].remove(matching_entries[0])
        self._write_db(data)
        self._handle_backup()
        return True

    def erase(self, condition: Query) -> int:
        """
        Erase all entries from the database that match the given condition.

        Args:
            condition (Query): A Query object defining the condition to match.

        Returns:
            int: The number of entries that were removed.
        """
        data = self._read_db()
        original_length = len(data["content"])
        data["content"] = [
            entry for entry in data["content"] if not condition.match(entry)
        ]
        removed_count = original_length - len(data["content"])

        if removed_count > 0:
            self._write_db(data)
            self._handle_backup()
            logger.debug(f"Erased {removed_count} entries from the database")

        return removed_count


db = EffortlessDB()
