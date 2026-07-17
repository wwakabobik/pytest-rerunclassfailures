# Pytest rerun class failures plugin


[![PyPI version](https://badge.fury.io/py/pytest-rerunclassfailures.svg)](https://badge.fury.io/py/pytest-rerunclassfailures) [![Linters](https://github.com/wwakabobik/pytest-rerunclassfailures/actions/workflows/master_linters.yml/badge.svg?branch=master)](https://github.com/wwakabobik/pytest-rerunclassfailures/actions/workflows/master_linters.yml) [![Tests](https://github.com/wwakabobik/pytest-rerunclassfailures/actions/workflows/master_tests.yml/badge.svg?branch=master)](https://github.com/wwakabobik/pytest-rerunclassfailures/actions/workflows/master_tests.yml) [![Coverage Status](https://coveralls.io/repos/github/wwakabobik/pytest-rerunclassfailures/badge.svg?branch=master)](https://coveralls.io/github/wwakabobik/pytest-rerunclassfailures?branch=master) [![codecov](https://codecov.io/gh/wwakabobik/pytest-rerunclassfailures/graph/badge.svg?token=F1I7TBGE5U)](https://codecov.io/gh/wwakabobik/pytest-rerunclassfailures) ![PyPI - License](https://img.shields.io/pypi/l/pytest-rerunclassfailures) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytest-rerunclassfailures) [![Downloads](https://static.pepy.tech/badge/pytest-rerunclassfailures)](https://pepy.tech/project/pytest-rerunclassfailures) [![Downloads](https://static.pepy.tech/badge/pytest-rerunclassfailures/month)](https://pepy.tech/project/pytest-rerunclassfailures) 


This plugin helps to rerun whole test classes that failed during the test run.
This means in case of failure of any class within the test class, the whole class will be rerun. 
Due to that, in case of failure plugin will fail fast: 
the rest of the tests in class will be aborted and will not be run. 
Instead of that, all tests from the class will be rerun starting first one.
The plugin supports proper class teardown and reset attribute of the class to initial values. 
So it will be reset before each rerun.

![pytest-rerunclassfailures](https://raw.githubusercontent.com/wwakabobik/pytest-rerunclassfailures/master/assets/pytest-rerunclassfailures.jpg)

## Installation

You can install the plugin via pip:

```bash
pip install pytest-rerunclassfailures
```


## Usage

After installation plugin ready to use, you do not need to pass extra options or add plugin to `pytest.ini`. Just run your tests as usual:

```bash
pytest tests --rerun-class-max=2
```

You always need pass `--rerun-class-max` with number of reruns for the class. By default, the plugin is disabled.

Other options you may use:
- `--rerun-class-max` - number of reruns for the class. Default is 0.
- `--rerun-delay` - delay between reruns in seconds. Default is 0.5.
- `--rerun-show-only-last` - show only last rerun results (without 'reruns' in log), by default is not used.
- `--hide-rerun-details` - hide rerun details in the log ('RERUNS' section in terminal), by default is not used.
- `--allow-rerunfailures` - allow running alongside `pytest-rerunfailures` instead of failing fast on startup; see [pytest-rerunfailures compatibility](#pytest-rerunfailures-compatibility) below.

```bash
PYTHONPATH=. pytest -s tests -p pytest_rerunclassfailures --rerun-class-max=3 --rerun-delay=1 --rerun-show-only-last
```

In some cases you may manage plugins manually, so, you can do it in two ways:

- Run your tests with plugin by passing by `-p` option:
```bash
PYTHONPATH=. pytest -s tests -p pytest-rerunclassfailures --rerun-class-max=3
```
- Add plugin to `pytest.ini` file:

```ini
[pytest]
plugins = pytest-rerunclassfailures
addopts = --rerun-class-max=3
```

To disable plugin (even ignoring passed `--rerun-class-max` option) use:

```bash
pytest test -p no:pytest-rerunclassfailures
```

## pytest-xdist support

Plugin supports `pytest-xdist` plugin. 
It means that you can run tests in parallel and rerun failed classes in parallel as well.
But please note that every class tests method should schedule to run in the same worker. 
So the plugin can rerun the whole class in the same worker.
To do so, you need to run your tests with `--dist=loadscope` option. 
Otherwise, there's no guarantee that results will be predictable.


## Known limitations
- Function- and class-scope fixtures used by the rerun class are genuinely torn down (their real finalizers run) and re-invoked between reruns. Module/package/session-scope fixtures are deliberately left untouched, since they may be shared with content outside the rerun class/cycle.
- A class attribute set purely as a side effect of a *function-scope* fixture whose return value is consumed as a test parameter (not stored on `self`) can still leak stale per-test state across reruns. This happens because pytest permanently memoizes the bound test-class instance on the underlying `Function` item itself, and this plugin reruns the same `Function` item objects rather than fresh ones - so a stale instance-level attribute set by a previous failed attempt's own test body can shadow the class-level attribute a fixture resets. This is independent of fixture teardown and is not fixed by this plugin.
- Due to `pytest-xdist` plugin limitations, report output will be thrown only when all tests in class are executed. This means that you will not see the output of the failed test until all tests in the class are rerun. Unfortunately, `pytest-xdist` plugin allows reporting results for only scheduled tests in scheduled order. Due to that, tests in class will be grouped by test, but not by rerun, as in regular run.

## pytest-rerunfailures compatibility

Both plugins hook `pytest_runtest_protocol`, so by default this plugin refuses to start (raises a clear `UsageError`) if `pytest-rerunfailures` is also active, to avoid a silent conflict.

Pass `--allow-rerunfailures` to run both together once you understand the caveat:
- Standalone (non-class) tests are unaffected and cooperate normally - a `pytest-rerunfailures` marker (`@pytest.mark.flaky`) or `--reruns` on a module-level test still reruns exactly as `pytest-rerunfailures` intends.
- A `pytest-rerunfailures` marker (or `--reruns`) on a test **method inside a class this plugin reruns** is silently superseded: the class-level rerun already governs that test, and the per-test marker never gets its own independent reruns.
