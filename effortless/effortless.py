# effortlessdb/effortless.py

_storage = {}

def set(obj):
    """Store an object in a simple storage."""
    _storage['object'] = obj

def get():
    """Retrieve the stored object."""
    return _storage.get('object', None)
