# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2024-10-21

### Added

- Introduced new `passes` method for custom filtering functions
- Added `is_type` method for type checking in queries
- Implements a blocking `finish_backup` method to databases to complete a backup before proceeding

## [1.1.0] - 2024-10-20

### Added

- Introduced new `filter` method to replace the previous `search` functionality
- Added `Query` and `Field` classes for more powerful and flexible querying
- Implemented a comprehensive set of query methods:
  - `equals`, `contains`, `startswith`, `endswith`
  - `greater_than`, `less_than`
  - `matches_regex`, `between_dates`, `fuzzy_match`
- Introduced support for lambdas in Queries to give granular filtering power
- Expanded test suite with extensive coverage for new features

### Changed

- Replaced `search` method with `filter` for more intuitive querying
- Updated documentation to reflect new querying capabilities

### Removed

- Removed `search` method in favor of `filter`

## [1.0.0] - 2024-10-19

### Added

- Fully-fledged configuration support has been implemented
  - Make an `EffortlessConfig` and `configure` your DB with it
  - Configurations like readonly, max_size, and required can be set to restrict
your database
  - Encryption, compression, and backups can be set to secure your database
  (partially implemented)
- More configuration has been automated (less effort for you!)
- `.effortless` format has moved to header/content instead of numerical

### Changed

- Effortless database objects have been renamed to EffortlessDBs

### Notes

- 1.0.0 is ***not*** compatible with any previous versions of Effortless.

## [0.1.0] - 2024-10-19

### Added

- Futureproofing for database configuration implementation
- Support for filename and directory modification for Effortless files
- Basic database manipulation functions: `get_all()`, `search()`, and `add()`
- `wipe()` function to clear the database while keeping the file
- Automatic database file creation if the specified db doesn't exist
- Support for searching through list values in the `search()` method
- Comprehensive testing suite for all functions and documentation
- Simplified usage via `from effortless import db`

### Changed

- Updated README.md to reflect new features and capabilities
