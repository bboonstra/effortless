# Databases should be [_Effortless_](https://bboonstra.github.io/Effortless).

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

Check the [quickstart](https://bboonstra.github.io/Effortless/docs/quickstart.html) for more details.

## Usage

We offer 3 tiers of effort when using our databases. If this is your first time
using a database, try out the [Effortless](https://bboonstra.github.io/Effortless/docs/effortless-usage.html) usage below.
If you are working on a simple project, you should take a look at the
[Basic](https://bboonstra.github.io/Effortless/docs/basic-usage.html) usage docs.
Overachievers may want to try our [Advanced](https://bboonstra.github.io/Effortless/docs/advanced-usage.html) features.

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
is_experienced = Query(lambda entry: len(entry["known_programming_languages"]) > 5)
GOATs = db.filter(is_bboonstra | is_experienced)
```

You've just filtered a thousand users into a couple with complex conditioning, and it was effortless.

### 🎓 Perfect for Learning

Whether you're a beginner or an experienced developer, Effortless provides a gentle learning curve without sacrificing power, making it an ideal choice for educational environments and rapid prototyping.

This project isn't a database; it's a philosophy:  data management should be simple, powerful, and... _Effortless_.
