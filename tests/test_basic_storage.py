# tests/test_basic_storage.py

from unittest import TestCase
from effortless import effortless as db


class TestBasic(TestCase):
    def test_set_get(self):
        assert db.get() is None
        db.set("test_object")
        assert db.get() == "test_object"
