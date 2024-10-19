# effortlessdb/effortless.py
import json
import os

_STORAGE_FILE = "db.effortless"


def set(obj):
    """Store an object in a persistent file-based storage."""
    with open(_STORAGE_FILE, "w") as f:
        json.dump(obj, f)


def get():
    """Retrieve the stored object from file-based storage."""
    if not os.path.exists(_STORAGE_FILE):
        return None
    with open(_STORAGE_FILE, "r") as f:
        return json.load(f)
