# Pytest rerun class failures plugin

[![PyPI version](https://badge.fury.io/py/pytest-rerunclassfailures.svg)](https://badge.fury.io/py/pytest-rerunclassfailures) [![Linters](https://github.com/wwakabobik/pytest-rerunclassfailures/actions/workflows/master_linters.yml/badge.svg?branch=master)](https://github.com/wwakabobik/pytest-rerunclassfailures/actions/workflows/master_linters.yml) [![Tests](https://github.com/wwakabobik/pytest-rerunclassfailures/actions/workflows/master_tests.yml/badge.svg?branch=master)](https://github.com/wwakabobik/pytest-rerunclassfailures/actions/workflows/master_tests.yml)

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
- Please note, this plugin still not supports rerun of the class setup method. This means that if you use class-scoped fixtures, they will not be rerun, only class attributes will be reset to initial values.
- Due to `pytest-xdist` plugin limitations, report output will be thrown only when all tests in class are executed. This means that you will not see the output of the failed test until all tests in the class are rerun. Unfortunately, `pytest-xdist` plugin allows reporting results for only scheduled tests in scheduled order. Due to that, tests in class will be grouped by test, but not by rerun, as in regular run.
- Never use this plugin with `pytest-rerunfailures` plugin. It will not work as expected.
