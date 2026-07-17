"""
Bootstrap subprocess coverage measurement for the subprocess-spawned pytest runs.

Used throughout this test suite (see conftest.py / test_arguments.py).

Newer coverage.py versions (7.11+) auto-install a startup .pth that reads
COVERAGE_PROCESS_START and calls coverage.process_startup() on interpreter start.
Older coverage.py versions still supported here (e.g. the last one compatible with
Python 3.9) don't ship that .pth automatically, so this directory is added to the
subprocess's PYTHONPATH to make Python import this sitecustomize module instead,
achieving the same effect regardless of the installed coverage.py version.

This is a no-op whenever COVERAGE_PROCESS_START isn't set (i.e. outside coverage runs).
"""

import coverage

coverage.process_startup()
