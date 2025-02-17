<!-- markdownlint-configure-file { "MD024": false } -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.1] - 2025-02-17

### Changed

- _run_command logger debug instead of info for ex:

### Fixed

- tailscale status line parsing

## [0.7.0] - 2025-01-05

### Added

- Support for tailscale addresses

### Removed

- Support for python version < 3.10

## [0.6.3] - 2025-01-05

### Added

- Support for ipv4net in templates

### Changed

- Updated tomli (2.0.2 -> 2.2.1)
- Updated pydantic-core (2.20.0 -> 2.20.1)
- Updated cryptography (42.0.8 -> 43.0.0)
- Updated pydantic (2.8.0 -> 2.8.2)
- Updated identify (2.5.36 -> 2.6.0)
- Updated wtforglib (1.0.1 -> 1.0.2)

## [0.6.2] - 2024-07-04

### Changed

- Use click.version_option, better format string for log

## [0.6.1] - 2024-07-04

### Changed

- Initialize logger according debug, verbose parameters and pass to app.

## [0.6.0] - 2024-07-03

### Changed

- Updated wtforglib (0.8.4 -> 1.0.0)
- Updated nslookup (1.7.0 -> 1.8.1)
- Updated typing-extensions (4.11.0 -> 4.12.2)
- Updated annotated-types (0.6.0 -> 0.7.0)
- Updated certifi (2024.2.2 -> 2024.6.2)
- Updated packaging (24.0 -> 24.1)
- Updated pycodestyle (2.11.1 -> 2.12.0)
- Updated pydantic-core (2.18.2 -> 2.20.0)
- Updated urllib3 (2.2.1 -> 2.2.2)
- Updated bandit (1.7.8 -> 1.7.9)
- Updated cryptography (42.0.7 -> 42.0.8)
- Updated flake8 (7.0.0 -> 7.1.0)
- Updated marshmallow (3.21.2 -> 3.21.3)
- Updated platformdirs (4.2.1 -> 4.2.2)
- Updated pydantic (2.7.1 -> 2.8.0)
- Updated requests (2.31.0 -> 2.32.3)
- Updated setuptools (69.5.1 -> 70.2.0)
- Updated authlib (1.3.0 -> 1.3.1)
- Updated coverage (7.5.1 -> 7.5.4)
- Updated dpath (2.1.6 -> 2.2.0)
- Updated flake8-comprehensions (3.14.0 -> 3.15.0)
- Updated more-itertools (10.2.0 -> 10.3.0)
- Updated pytest (8.2.0 -> 8.2.2)
- Updated requests-cache (1.2.0 -> 1.2.1)
- Updated mypy (1.10.0 -> 1.10.1)
- Updated safety (3.2.0 -> 3.2.3)
- Updated sphinx-autodoc-typehints (2.1.0 -> 2.2.2)
- Updated testfixtures (8.2.0 -> 8.3.0)

## [0.5.6] - 2024-05-11

### Added

- app rules for ufw

### Changed

- poetry updates

### Fixed

- Corrected load config file to use base for multiple configs
- PT001 errors


## [0.5.5] - 2023-11-24

### Added

- Log caught exceptions

### Changed

- poetry updates
- Use wtforglib template writer

### Fixed

- Raise exception when dns lookup fails, so templates will not upd…

## [0.2.0] - 2023-03-22

### Added

- Support global_whites whitelist

### Changed

- poetry updates

## [0.1.4] - 2023-03-04

### Changed

- poetry updates

## [0.1.3] - 2023-01-28

### Changed

- poetry updates

### Fixed

- Sort mapping lists


## [0.1.2] - 2023-01-26

### Changed

- poetry updates

### Fixed

- Sort whitelist

## [0.1.1] - 2023-01-23

- First Release
