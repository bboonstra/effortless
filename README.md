# Databases should be _Effortless_.

[![Publish Package](https://github.com/bboonstra/Effortless/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/bboonstra/Effortless/actions/workflows/publish.yml)
[![Run Tests](https://github.com/bboonstra/Effortless/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/bboonstra/Effortless/actions/workflows/test.yml)

Effortless has one objective: be the easiest database.
It's perfect for beginners, but effortless for anyone.

## Quickstart

You can install Effortless easily, if you have
[pip](https://pip.pypa.io/en/stable/installation/) and
[Python 3.9 or higher](https://www.python.org/downloads/) installed.

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
from effortless import db, Field

# Add items to the database
db.add({"name": "Alice", "age": 30})
db.add({"name": "Bob", "age": 25})

# Get all items from the DB
all_items = db.get_all()
print(all_items)
# Output: {'1': {'name': 'Alice', 'age': 30}, '2': {'name': 'Bob', 'age': 25}}

# Get items based on a field
# This will get all items where their name is Alice
result = db.filter(Field("name").equals("Alice"))
print(result)  # Output: {'1': {'name': 'Alice', 'age': 30}}

# Wipe the database
db.wipe()
print(db.get_all())  # Output: {}
```

### Basic Usage

```python
from effortless import EffortlessDB, Field

# Create a new Effortless instance
db = EffortlessDB()

# Add items to the database
db.add({"name": "Charlie", "age": 35})
db.add({"name": "David", "age": 28})

# Filter items
result = db.filter(Field("age").greater_than(30))
print(result)  # Output: {'1': {'name': 'Charlie', 'age': 35}}

```

### Advanced Usage

```python
from effortless import EffortlessDB, EffortlessConfig, Field, Query

# Create a new Effortless instance with a custom directory
db = EffortlessDB("advanced_db")
db.set_directory("/path/to/custom/directory")

# Add multiple items
db.add({"id": 1, "name": "Eve", "skills": ["Python", "JavaScript"], "joined": "2023-01-15"})
db.add({"id": 2, "name": "Frank", "skills": ["Java", "C++"], "joined": "2023-02-20"})
db.add({"id": 3, "name": "Grace", "skills": ["Python", "Ruby"], "joined": "2023-03-10"})

# Complex filtering
python_devs = db.filter(
    Field("skills").contains("Python") & 
    Field("joined").between_dates("2023-01-01", "2023-02-28")
)
print(python_devs)

# Custom query using Query class
custom_query = Query(lambda item: len(item["skills"]) > 1 and "Python" in item["skills"])
multi_skill_python_devs = db.filter(custom_query)
print(multi_skill_python_devs)

# Update configuration
db.configure(EffortlessConfig({"readonly": True}))
# The database contents are now read-only
db.add({"Anything": "will not work"}) # Raises an error

```

## New Filtering Capabilities

Effortless 1.1.0 introduces powerful filtering capabilities using the `Field` class:

- `equals`: Exact match
- `contains`: Check if a value is in a string or list
- `startswith`, `endswith`: String prefix and suffix matching
- `greater_than`, `less_than`: Numeric comparisons
- `matches_regex`: Regular expression matching
- `between_dates`: Date range filtering
- `fuzzy_match`: Approximate string matching

You can combine these filters using `&` (AND) and `|` (OR) operators for complex queries.

```python
result = db.filter(
    (Field("age").greater_than(25) & Field("skills").contains("Python")) |
    Field("name").startswith("A")
)
```

For even more flexibility, you can use the `Query` class with a custom lambda function:

```python
from effortless import Query

custom_query = Query(lambda item: len(item["name"]) > 5 and item["age"] % 2 == 0)
result = db.filter(custom_query)
```

These new filtering capabilities make Effortless more powerful while maintaining its simplicity and ease of use.

## Why Effortless?

If you're actually reading this section, it seems like you don't care about the whole "effortless" part. If you did, you'd already have your own million-dollar startup with one of our databases by now. So, here's some other reasons Effortless stands out:

### 🛡️ Safety First

All your data is safe, lossless, and locally stored by default. You can begin persistent, automatic backups, keyed database encryption, and more with a couple lines of Python.

```py
new_configuration = EffortlessConfig()
new_configuration.backup = "/path/to/backup"
db.configure(new_configuration)
```

All your data is now automatically backed up to the specified path until you edit the configuration again.

### 🔍 Powerful Querying

Effortless introduces a unique and intuitive object-oriented filter system. You can create a reusable Field condition with logical operators to find anything from your database.

```python
is_bboonstra = Field("username").equals("bboonstra")
is_experienced = Query(lambda item: len(item["known_programming_languages"]) > 5)
GOATs = db.filter(is_bboonstra | is_experienced)
```

You've just filtered a thousand users into a couple with complex conditioning, and it was effortless.

### 🎓 Perfect for Learning

Whether you're a beginner or an experienced developer, Effortless provides a gentle learning curve without sacrificing power, making it an ideal choice for educational environments and rapid prototyping.

This project isn't a database; it's a philosophy:  data management should be simple, powerful, and... _Effortless_.
