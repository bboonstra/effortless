import unittest
import tempfile
import shutil
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
        self.assertFalse(config.debug)
        self.assertEqual(config.requires, [])
        self.assertIsNone(config.max_size)
        self.assertEqual(config.v, 1)
        self.assertIsNone(config.backup)
        self.assertEqual(config.backup_interval, 1)
        self.assertFalse(config.encrypted)
        self.assertFalse(config.compressed)
        self.assertFalse(config.readonly)

    def test_configure_method(self):
        new_config = {
            "dbg": True,
            "rq": ["name", "age"],
            "ms": 100,
            "bp": "/backup/path",
            "bpi": 5,
            "enc": False,
            "cmp": False,
            "ro": True,
        }
        self.db.wipe()
        self.db.configure(EffortlessConfig(new_config))

        config = self.db.config
        self.assertTrue(config.debug)
        self.assertEqual(config.requires, ["name", "age"])
        self.assertEqual(config.max_size, 100)
        self.assertEqual(config.v, 1)
        self.assertEqual(config.backup, "/backup/path")
        self.assertEqual(config.backup_interval, 5)
        self.assertFalse(config.encrypted)
        self.assertFalse(config.compressed)
        self.assertTrue(config.readonly)

    def test_invalid_configuration(self):
        with self.assertRaises(TypeError):
            self.db.configure("invalid")  # type: ignore

    def test_required_fields(self):
        self.db.configure(EffortlessConfig({"rq": ["name"]}))
        self.db.add({"name": "Alice", "age": 30})  # This should work

        with self.assertRaises(ValueError):
            self.db.add({"age": 25})  # This should raise an error

    def test_max_size_limit(self):
        self.db.wipe()
        self.db.configure(EffortlessConfig({"ms": 0.001}))  # Set max size to 1 KB
        
        # This should work
        self.db.add({"small": "data"})
        
        # This should raise an error
        large_data = {"large": "x" * 1000}  # Approximately 1 KB
        with self.assertRaises(ValueError):
            self.db.add(large_data)

    def test_readonly_mode(self):
        self.db = EffortlessDB()
        self.db.configure(EffortlessConfig({"ro": True}))
        with self.assertRaises(ValueError):
            self.db.add({"name": "Alice"})

    def test_configuration_persistence(self):
        new_config = {"dbg": True, "rq": ["name"], "ms": 100, "v": 1}
        self.db.configure(EffortlessConfig(new_config))

        # Create a new instance with the same storage
        new_db = EffortlessDB()
        new_db.set_directory(self.test_dir)
        new_db.set_storage("test_db")

        config = new_db.config
        self.assertTrue(config.debug)
        self.assertEqual(config.requires, ["name"])
        self.assertEqual(config.max_size, 100)
        self.assertEqual(config.v, 1)

    def test_invalid_configuration_values(self):
        with self.assertRaises(ValueError):
            EffortlessConfig({"ms": -1})
        with self.assertRaises(ValueError):
            EffortlessConfig({"v": 0})
        with self.assertRaises(ValueError):
            EffortlessConfig({"bpi": 0})


if __name__ == "__main__":
    unittest.main()
