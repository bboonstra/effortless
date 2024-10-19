# Databases should be _Effortless_.

[![Publish Package](https://github.com/bboonstra/Effortless/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/bboonstra/Effortless/actions/workflows/publish.yml)
[![Run Tests](https://github.com/bboonstra/Effortless/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/bboonstra/Effortless/actions/workflows/test.yml)

Effortless has one objective: be the easiest database.
It's perfect for beginners, but effortless for anyone.

## Quickstart

You can install Effortless easily, if you have [pip](https://pip.pypa.io/en/stable/installation/) and [Python 3.9 or higher](https://www.python.org/downloads/) installed.

```bash
pip install effortless
```

## Usage

We offer 3 tiers of effort when using our databases. If this is your first time
using a database, try out the [Effortless](#effortless-usage) usage below.
If you are working on a simple project, you should take a look at the
[Basic](#basic-usage) usage docs.
Overachievers may want to try our [Advanced](#advanced-usage) features.

### Effortless Usage

```python
from effortless import db

# Add items to the database
db.add({"name": "Alice", "age": 30})
db.add({"name": "Bob", "age": 25})

# Search for items
result = db.search({"name": "Alice"})
print(result)  # Output: {'1': {'name': 'Alice', 'age': 30}}

# Get all items
all_items = db.get_all()
print(all_items)
# Output: {'1': {'name': 'Alice', 'age': 30}, '2': {'name': 'Bob', 'age': 25}}

# Wipe the database
db.wipe()
print(db.get_all())  # Output: {}
```

### Basic Usage

```python
from effortless import Effortless

# Create a new Effortless instance
db = Effortless()

# Add items to the database
db.add({"name": "Charlie", "age": 35})
db.add({"name": "David", "age": 28})

# Search for items
result = db.search({"age": 28})
print(result)  # Output: {'2': {'name': 'David', 'age': 28}}

# Get all items
all_items = db.get_all()
print(all_items)
# Output: {'1': {'name': 'Charlie', 'age': 35}, '2': {'name': 'David', 'age': 28}}
```

### Advanced Usage

```python
from effortless import Effortless

# Create a new Effortless instance with a custom directory
db = Effortless("advanced_db")
db.set_directory("/path/to/custom/directory")

# Add multiple items
db.add({"id": 1, "name": "Eve", "skills": ["Python", "JavaScript"]})
db.add({"id": 2, "name": "Frank", "skills": ["Java", "C++"]})
db.add({"id": 3, "name": "Grace", "skills": ["Python", "Ruby"]})

# Complex search
python_devs = db.search({"skills": "Python"})
print(python_devs)
# Output: {'1': {'id': 1, 'name': 'Eve', 'skills': ['Python', 'JavaScript']},
#          '3': {'id': 3, 'name': 'Grace', 'skills': ['Python', 'Ruby']}}

# Update configuration
db.configure({"index_fields": ["id", "name"]})

# Wipe the database
db.wipe()
print(db.get_all())  # Output: {}
```

## Why Effortless?

Not only is storing, retrieving, and managing data is as simple is it can be,
Effortless is also:

### - Cross platform

Effortless DBs work on any device supporting Python and DBs can be copied across
devices.

### - Safe

All DB data is safe, lossless, local, and recoverable by default.

### - Scaling

Our DBs have deep code support for batch functions.

### - Clear

We take pride in our documentation, so that learning takes minimal effort.

- ### Broad

All that's required to use Effortless is Python >= 3.9.

### - Compact

Our code is compact, both in package size, dependencies, and db size.

[![Lines of Code](https://img.shields.io/github/languages/code-size/bboonstra/Effortless)](https://github.com/bboonstra/Effortless)
[![Package Size](https://img.shields.io/github/repo-size/bboonstra/Effortless)](https://github.com/bboonstra/Effortless)
[![Dependencies](https://img.shields.io/librariesio/github/bboonstra/Effortless)](https://libraries.io/github/bboonstra/Effortless)

---

## Contributing

Writing code takes a lot of effort! Check out [CONTRIBUTING.md](CONTRIBUTING.md)
for information.
