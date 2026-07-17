# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-07-17

### Added
- Real use of `pydantic` (v2) to validate plugin CLI options; out-of-range values (e.g. negative `--rerun-class-max`/`--rerun-delay`) now raise a clear usage error instead of being silently accepted
- Class-scope (and function-scope) fixtures are now genuinely torn down and re-invoked between class reruns, instead of only having plain instance attributes snapshotted/restored, using pytest's own SetupState finalizer chain (no manual fixture bookkeeping)
- A class attribute lazily created during a rerun cycle (e.g. by a fixture's `if not hasattr(request.cls, "x"): ...` guard) is now removed between reruns instead of leaking whatever state a previous, aborted attempt left it in

### Changed
- Dropped Python 3.8 support (EOL); added Python 3.13 and 3.14 to the supported/tested versions
- Pinned `pydantic>=2,<3` (was previously unpinned and unused)

### Fixed
- Fixed a logging format bug (`%` typo) that broke a debug log message
- Fixed `setup.py`'s stale `pytest11` entry point and `setup.cfg`'s invalid `version = attr:` value
- Fixed a crash (`assert not self._finalizers`) when a class-, module-, or session-scope fixture failed during setup and the class was rerun; module/session-scope fixtures are now correctly never retried (matching their scope contract) instead of being silently (and unsafely) retried

## [0.0.1] - 2024-03-19

### Added
- Initial version

## [0.0.2] - 2024-03-26

### Added
- Test suite added to cover most of the functionality
- Added complete readme
- Plugin setup has been updated


## [0.0.3] - 2024-03-27

### Fixed
- Possible out of range error when rerunning tests more one time

## [0.0.4] - 2024-03-28

### Fixed
- Fix reporting in case of abort: pass skipped status to the report

## [0.0.5] - 2024-03-29

### Updated
- Added missed typing for plugin functions and their arguments
- Add terminal reporter for reruns
- Added xdist for package testing
- Add more debug logging

## [0.1.0] - 2024-03-29

### Updated
- README.md updated
- Added more tests to achieve 100% coverage (including non-reachable code via mocks)
- Added coverage collection and reporting

## [0.1.1] - 2024-04-24

### Fixed
- Fixed proper setting of result outcome for reruns in case of different rerun length

### Updated
- Requirements bumped to the latest versions
