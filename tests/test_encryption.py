import unittest
import tempfile
import shutil
import os
from effortless import EffortlessDB, EffortlessConfig
from cryptography.fernet import InvalidToken, Fernet


class TestEncryption(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = EffortlessDB()
        self.db.set_directory(self.test_dir)
        self.db.set_storage("test_db")
        self.db.wipe()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_encryption_key_property(self):
        self.assertIsNone(
            self.db.encryption_key, "Initial encryption key should be None"
        )

        self.db.encryption_key = "test_key"
        self.assertEqual(
            self.db.encryption_key, "test_key", "Encryption key should be set correctly"
        )

        self.db.unencrypt()
        self.assertIsNone(self.db.encryption_key, "Encryption key should be unset")

    def test_set_encryption_key(self):
        with self.assertRaises(TypeError, msg="Non-string key should raise TypeError"):
            self.db.encrypt(123)  # type: ignore

        self.db.encrypt("test_key")
        self.assertEqual(
            self.db._encryption_key,
            "test_key",
            "Encryption key should be set correctly",
        )

        self.db.unencrypt()
        self.assertIsNone(self.db._encryption_key, "Encryption key should be unset")

    def test_encrypt_decrypt_data(self):
        key = "test_key"
        data = {"test": "data"}

        encrypted = self.db._encrypt_data(data, key)
        self.assertNotEqual(
            encrypted, str(data), "Encrypted data should differ from original"
        )

        decrypted = self.db._decrypt_data(encrypted, key)
        self.assertEqual(decrypted, data, "Decrypted data should match original")

        with self.assertRaises(
            InvalidToken, msg="Decryption with wrong key should fail"
        ):
            self.db._decrypt_data(encrypted, "wrong_key")

    def test_get_fernet_key(self):
        key = "short_key"
        fernet_key = self.db._get_fernet_key(key)
        self.assertEqual(
            len(fernet_key),
            44,
            "Fernet key should be 44 bytes long when base64 encoded",
        )
        self.assertNotEqual(
            fernet_key, key.encode(), "Fernet key should differ from original"
        )

        long_key = "this_is_a_very_long_key_that_exceeds_32_bytes"
        fernet_key_long = self.db._get_fernet_key(long_key)
        self.assertEqual(
            len(fernet_key_long),
            44,
            "Fernet key should be 44 bytes long when base64 encoded",
        )

        # Test that the key is valid for Fernet
        from cryptography.fernet import Fernet

        try:
            Fernet(fernet_key)
        except ValueError:
            self.fail("Generated key is not a valid Fernet key")

    def test_fernet_key_validity(self):
        key = "test_key"
        fernet_key = self.db._get_fernet_key(key)
        try:
            Fernet(fernet_key)
        except ValueError:
            self.fail("Generated key is not a valid Fernet key")

    def test_encryption_workflow(self):
        # Configure encryption
        self.db.encrypt("initial_key")
        self.db.configure(EffortlessConfig(encrypted=True))

        # Add data
        self.db.add({"test": "encrypted_data"})

        # Verify data is encrypted in storage
        with open(self.db._storage_file, "r") as f:
            raw_data = f.read()
        self.assertNotIn(
            "encrypted_data", raw_data, "Data should not be stored in plaintext"
        )

        # Retrieve and verify data
        data = self.db.get_all()
        self.assertEqual(
            data,
            [{"test": "encrypted_data"}],
            "Retrieved data should be decrypted correctly",
        )

        # Change encryption key
        self.db.encrypt("new_key")

        # Verify data can still be retrieved with new key
        data = self.db.get_all()
        self.assertEqual(
            data, [{"test": "encrypted_data"}], "Data should be accessible with new key"
        )

        db_using_old_key = EffortlessDB(encryption_key="initial_key")
        db_using_old_key.set_directory(self.test_dir)
        with self.assertRaises(
            ValueError, msg="Old key should not work after changing"
        ):
            db_using_old_key.set_storage("test_db")
            db_using_old_key.get_all()

    def test_encryption_with_compression(self):
        self.db.encrypt("test_key")
        self.db.configure(EffortlessConfig(encrypted=True, compressed=True))

        large_data = {"large": "x" * 1000}
        self.db.add(large_data)

        # Verify data is compressed and encrypted
        file_size = os.path.getsize(self.db._storage_file)
        self.assertLess(
            file_size, 1000, "File size should be less than uncompressed data"
        )

        # Retrieve and verify data
        data = self.db.get_all()
        self.assertEqual(
            data,
            [large_data],
            "Retrieved data should match original after decompression and decryption",
        )

    def test_encryption_key_change(self):
        self.db.encrypt("initial_key")
        self.db.configure(EffortlessConfig(encrypted=True))
        self.db.add({"test": "data"})

        # Change the encryption key
        self.db.encrypt("new_key")

        # Verify data can be accessed with the new key
        data = self.db.get_all()
        self.assertEqual(
            data,
            [{"test": "data"}],
            "Data should be accessible with new key after re-encryption",
        )

        # Verify old key no longer works
        old_db = EffortlessDB(encryption_key="initial_key")
        old_db.set_directory(self.test_dir)
        
        with self.assertRaises(ValueError, msg="Old key should not work after changing"):
            old_db.set_storage("test_db")
            old_db.get_all()

        # Verify new key works with a fresh instance
        new_db = EffortlessDB(encryption_key="new_key")
        new_db.set_directory(self.test_dir)
        new_db.set_storage("test_db")
        
        new_data = new_db.get_all()
        self.assertEqual(
            new_data,
            [{"test": "data"}],
            "Data should be accessible with new key in a fresh instance",
        )

    def test_encryption_key_persistence(self):
        self.db.encrypt("persistent_key")
        self.db.configure(EffortlessConfig(encrypted=True))
        self.db.add({"test": "persistent_data"})

        # Create a new instance with the same storage
        new_db = EffortlessDB(encryption_key="persistent_key")
        new_db.set_directory(self.test_dir)
        new_db.set_storage("test_db")
        new_db.configure(EffortlessConfig(encrypted=True))

        data = new_db.get_all()
        self.assertEqual(
            data,
            [{"test": "persistent_data"}],
            "Data should be accessible with same key in new instance",
        )


if __name__ == "__main__":
    unittest.main()
