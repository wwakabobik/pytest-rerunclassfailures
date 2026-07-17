# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-07-17

### Added
- Real use of `pydantic` (v2) to validate plugin CLI options; out-of-range values (e.g. negative `--rerun-class-max`/`--rerun-delay`) now raise a clear usage error instead of being silently accepted
- Class-scope (and function-scope) fixtures are now genuinely torn down and re-invoked between class reruns, instead of only having plain instance attributes snapshotted/restored, using pytest's own SetupState finalizer chain (no manual fixture bookkeeping)
- A class attribute lazily created during a rerun cycle (e.g. by a fixture's `if not hasattr(request.cls, "x"): ...` guard) is now removed between reruns instead of leaking whatever state a previous, aborted attempt left it in
- New `--allow-rerunfailures` option: the plugin now detects `pytest-rerunfailures` (both hook `pytest_runtest_protocol`) and prints a one-time message explaining that a rerunfailures marker on a method inside a class this plugin reruns is silently superseded by the class-level rerun; pass the flag to silence it. The suite is never blocked from running either way. Standalone (non-class) tests now cooperate correctly with `pytest-rerunfailures` regardless of the flag, since this plugin defers to other `pytest_runtest_protocol` implementations for items outside its scope instead of always claiming them
- The plugin now detects `pytest-xdist` running with `--dist=load` (its default when `-n`/`--numprocesses` is passed without `--dist`) and prints a one-time message: this mode doesn't guarantee every method of a class lands on the same worker, so a class rerun can silently miss sibling tests and produce inconsistent results between runs. No flag to silence it - use `--dist=loadscope` or `--dist=loadfile` instead

### Changed
- Dropped Python 3.8 support (EOL); added Python 3.13 and 3.14 to the supported/tested versions
- Pinned `pydantic>=2.4` (was previously unpinned and unused; `>=2.4` also avoids CVE-2024-3772, a ReDoS in pydantic's email validation)
- Test suite coverage measurement now correctly instruments the subprocess-spawned pytest runs most of the suite uses (previously silently under-measured to ~42% both locally and in CI, since coverage.py never measures a child process without `COVERAGE_PROCESS_START` + `parallel=true`)
- Coverage is now measured with `branch = true` (not just statement coverage); this caught two untested branches in `pytest_terminal_summary`, now covered - the suite reaches 100% statement and branch coverage on pytest 7.2/8.4/9.1 across Python 3.9-3.14

### Fixed
- Fixed a logging format bug (`%` typo) that broke a debug log message
- Fixed `setup.py`'s stale `pytest11` entry point and `setup.cfg`'s invalid `version = attr:` value
- Fixed a crash (`assert not self._finalizers`) when a class-, module-, or session-scope fixture failed during setup and the class was rerun; module/session-scope fixtures are now correctly never retried (matching their scope contract) instead of being silently (and unsafely) retried
- Fixed the last remaining state-leak between reruns: pytest permanently memoizes the bound test-class instance on the `Function` item itself (`Function._instance`/`_obj`), and this plugin reruns the same `Function` item objects rather than fresh ones - so a stale instance-level attribute set by a previous failed attempt's own test body could shadow the class-level attribute a fixture resets. The plugin now drops `_instance`/`_obj` between reruns so a genuinely fresh instance is created next time, same as real pytest between separate test runs

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
