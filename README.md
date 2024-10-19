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

```python3
import effortless as db
db.set("test")
print(db.get())
"test"
```

## Contributing
Writing code takes a lot of effort! Check out [CONTRIBUTING.md](CONTRIBUTING.md) for information.
