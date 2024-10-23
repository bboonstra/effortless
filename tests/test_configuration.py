import unittest
import tempfile
import shutil
import os
from effortless import EffortlessDB, EffortlessConfig


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = EffortlessDB()
        self.db.set_directory(self.test_dir)
        self.db.set_storage("test_db")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_default_configuration(self):
        config = self.db.config
        self.assertFalse(config.debug, "Debug mode should be off by default")
        self.assertEqual(
            config.required_fields, [], "No fields should be required by default"
        )
        self.assertIsNone(config.max_size, "Max size should be None by default")
        self.assertEqual(
            config.version,
            config.CURRENT_VERSION,
            "Version should be latest by default",
        )
        self.assertIsNone(config.backup_path, "Backup path should be None by default")
        self.assertEqual(
            config.backup_interval, 1, "Backup interval should be 1 by default"
        )
        self.assertFalse(config.encrypted, "Encryption should be off by default")
        self.assertFalse(config.compressed, "Compression should be off by default")
        self.assertFalse(config.readonly, "Read-only mode should be off by default")

    def test_configure_method(self):
        new_config = EffortlessConfig(
            debug=True,
            required_fields=["name", "age"],
            max_size=100,
            backup_path="/backup/path",
            backup_interval=5,
            encrypted=False,
            compressed=False,
            readonly=True,
        )
        self.db.wipe()
        self.db.configure(new_config)

        config = self.db.config
        self.assertTrue(config.debug, "Debug mode should be on after configuration")
        self.assertEqual(
            config.required_fields,
            ["name", "age"],
            "Required fields should be set to name and age",
        )
        self.assertEqual(config.max_size, 100, "Max size should be set to 100")
        self.assertEqual(
            config.version, EffortlessConfig.CURRENT_VERSION, "Version should be latest"
        )
        self.assertEqual(
            config.backup_path,
            "/backup/path",
            "Backup path should be set to /backup/path",
        )
        self.assertEqual(
            config.backup_interval, 5, "Backup interval should be set to 5"
        )
        self.assertFalse(config.encrypted, "Encryption should remain off")
        self.assertFalse(config.compressed, "Compression should remain off")
        self.assertTrue(config.readonly, "Read-only mode should be on")

    def test_invalid_configuration(self):
        with self.assertRaises(
            TypeError,
            msg="Configuring with a non-EffortlessConfig object should raise TypeError",
        ):
            self.db.configure("invalid")  # type: ignore

    def test_required_fields(self):
        self.db.configure(EffortlessConfig(required_fields=["name"]))
        self.db.add({"name": "Alice", "age": 30})  # This should work
        with self.assertRaises(
            ValueError,
            msg="Adding an entry without a required field should raise ValueError",
        ):
            self.db.add({"age": 25})  # This should raise an error

    def test_max_size_limit(self):
        self.db.wipe()
        self.db.configure(EffortlessConfig(max_size=0.001))  # Set max size to 1 KB

        # This should work
        self.db.add({"small": "data"})

        # This should raise an error
        large_data = {"large": "x" * 1000}  # Approximately 1 KB
        with self.assertRaises(
            ValueError, msg="Adding data exceeding max size should raise ValueError"
        ):
            self.db.add(large_data)

    def test_readonly_mode(self):
        self.db = EffortlessDB()
        self.db.configure(EffortlessConfig(readonly=True))
        with self.assertRaises(
            ValueError, msg="Adding to a read-only database should raise ValueError"
        ):
            self.db.add({"name": "Alice"})

    def test_configuration_persistence(self):
        new_config = EffortlessConfig(
            debug=True,
            required_fields=["name"],
            max_size=100,
            version="1.2.0",
        )
        first_db = EffortlessDB("first_db")
        first_db.configure(new_config)

        # Create a new instance with the same storage
        new_db = EffortlessDB("test_db")
        new_db.set_directory(self.test_dir)
        new_db._write_db(first_db._read_db())
        new_db._autoconfigure()
        config = new_db.config

        self.assertTrue(
            config.debug, "Debug mode should persist across database instances"
        )
        self.assertEqual(
            config.required_fields,
            ["name"],
            "Required fields should persist across database instances",
        )
        self.assertEqual(
            config.max_size, 100, "Max size should persist across database instances"
        )
        self.assertEqual(
            config.version, config.CURRENT_VERSION, "Version should upgrade across database instances"
        )

    def test_invalid_configuration_values(self):
        with self.assertRaises(
            ValueError, msg="Negative max size should raise ValueError"
        ):
            EffortlessConfig(max_size=-1)
        with self.assertRaises(ValueError, msg="Version 0 should raise ValueError"):
            EffortlessConfig(version="invalid")
        with self.assertRaises(
            ValueError, msg="Backup interval 0 should raise ValueError"
        ):
            EffortlessConfig(backup_interval=0)

    def test_backup_interval(self):
        # Configure the database with a backup path
        backup_path = tempfile.mkdtemp()  # Create a temporary directory for backups
        new_config = EffortlessConfig(
            debug=True,
            backup_path=backup_path,  # Set backup path
            backup_interval=1,  # Backup after every operation
        )
        self.db.configure(new_config)

        # Assert that the backup path is properly configured
        self.assertEqual(
            self.db.config.backup_path,
            backup_path,
            "Backup path should be set correctly",
        )

        # Add an entry to trigger a backup
        self.db.add({"name": "Alice", "age": 30})

        backup_file = os.path.join(backup_path, "test_db.effortless")
        self.assertFalse(
            os.path.exists(backup_file),
            "DB should not be backed up after 1 operation if backup_interval == 2.",
        )

        # Add another entry to trigger a backup again
        self.db.add({"name": "Bob", "age": 25})

        # Check if the backup file still exists and has been updated
        self.assertTrue(
            os.path.exists(backup_file),
            "Backup file should exist after adding the second entry.",
        )

        # Clean up the backup directory
        shutil.rmtree(backup_path, ignore_errors=True)

    def test_validate_db(self):
        # Test max_size validation
        self.db.wipe()
        small_config = EffortlessConfig(max_size=0.001)  # 1 KB
        self.db.configure(small_config)
        self.db.add({"small": "data"})

        # This should work (database is still small)
        small_config.validate_db(self.db)

        # Now let's make the database larger than the config allows
        large_config = EffortlessConfig(max_size=1)  # 1 MB
        self.db.configure(large_config)
        self.db.add({"large": "x" * 1000000})  # Add 1 MB of data

        with self.assertRaises(
            ValueError, msg="Should raise ValueError when database exceeds max_size"
        ):
            small_config.validate_db(self.db)

        # Test required_fields validation
        self.db.wipe()
        no_required_fields_config = EffortlessConfig()
        self.db.configure(no_required_fields_config)
        self.db.add({"name": "Alice"})
        self.db.add({"age": 30})

        # This should work (no required fields)
        no_required_fields_config.validate_db(self.db)

        # Now let's add a required field
        required_fields_config = EffortlessConfig(required_fields=["name"])

        with self.assertRaises(
            ValueError,
            msg="Should raise ValueError when an entry is missing a required field",
        ):
            required_fields_config.validate_db(self.db)

        # Fix the database to comply with the new config
        self.db.wipe()
        self.db.add({"name": "Alice"})
        self.db.add({"name": "Bob", "age": 30})

        # This should now work
        required_fields_config.validate_db(self.db)

        # Test with multiple required fields
        multiple_required_fields_config = EffortlessConfig(
            required_fields=["name", "age"]
        )

        with self.assertRaises(
            ValueError,
            msg="Should raise ValueError when an entry is missing one of multiple required fields",
        ):
            multiple_required_fields_config.validate_db(self.db)

        # Fix the database again
        self.db.wipe()
        self.db.add({"name": "Alice", "age": 25})
        self.db.add({"name": "Bob", "age": 30})

        # This should now work with multiple required fields
        multiple_required_fields_config.validate_db(self.db)

    def test_config_setter_validation(self):
        # Set up a database with some entries
        self.db.wipe()
        self.db.add({"name": "Alice", "age": 30})
        self.db.add({"name": "Bob"})

        # Attempt to set a configuration that's incompatible with the current database state
        incompatible_config = EffortlessConfig(
            required_fields=["name", "age"], max_size=0.0001
        )  # 0.1 KB

        with self.assertRaises(
            ValueError, msg="Setting an incompatible config should raise ValueError"
        ):
            self.db.configure(incompatible_config)

        # Ensure the original configuration is unchanged
        self.assertNotIn("age", self.db.config.required_fields)
        self.assertIsNone(self.db.config.max_size)

        # Set a compatible configuration
        compatible_config = EffortlessConfig(
            required_fields=["name"], max_size=1
        )  # 1 MB
        self.db.configure(compatible_config)

        # Verify that the new configuration was applied
        self.assertEqual(self.db.config.required_fields, ["name"])
        self.assertEqual(self.db.config.max_size, 1)


if __name__ == "__main__":
    unittest.main()
