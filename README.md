# Pytest rerun class failures plugin

[![Linters](https://github.com/wwakabobik/pytest-rerunclassfailures/actions/workflows/master_linters.yml/badge.svg?branch=master)](https://github.com/wwakabobik/pytest-rerunclassfailures/actions/workflows/master_linters.yml) [![Tests](https://github.com/wwakabobik/pytest-rerunclassfailures/actions/workflows/master_tests.yml/badge.svg?branch=master)](https://github.com/wwakabobik/pytest-rerunclassfailures/actions/workflows/master_tests.yml)

This plugin helps to rerun whole test classes that failed during the test run.
This means in case of failure of any class within the test class, the whole class will be rerun. 
Due to that, in case of failure plugin will fail fast: 
the rest of the tests in class will be aborted and will not be run. 
Instead of that, all tests from the class will be rerun starting first one.
The plugin supports proper class teardown and reset attribute of the class to initial values. 
So it will be reset before each rerun.

![pytest-rerunclassfailures](https://raw.githubusercontent.com/wwakabobik/pytest-rerunclassfailures/master/src/assets/pytest-rerunclassfailures.jpg)

## Installation
TBD (not published yet)


## Usage

Run your tests with plugin by passing by `-p` option:
```bash
PYTHONPATH=. pytest -s tests -p pytest_rerunclassfailures --rerun-class-max=3
```
Add plugin to `pytest.ini` file:

```ini
[pytest]
plugins = pytest_rerunclassfailures
addopts = --rerun-class-max=3
```

You always can pass `--rerun-class-max` with number of reruns for the class. By default, the plugin is disabled.

Other options you may use:
- `--rerun-class-max` - number of reruns for the class. Default is 0.
- `--rerun-delay` - delay between reruns in seconds. Default is 0.5.
- `--rerun-show-only-last` - show only last rerun results (without 'reruns' in log), by default is not used.

```bash
PYTHONPATH=. pytest -s tests -p pytest_rerunclassfailures --rerun-class-max=3 --rerun-delay=1 --rerun-show-only-last
```

## XDist support

Plugin supports `pytest-xdist` plugin. 
It means that you can run tests in parallel and rerun failed classes in parallel as well.
But please note that every class tests method should schedule to run in the same worker. 
So the plugin can rerun the whole class in the same worker.
To do so, you need to run your tests with `--dist=loadscope` option. 
Otherwise, there's no guarantee that results will be predictable.


## Known limitations
- Please note, this plugin still not supports rerun of the class setup method. This means that if you use class-scoped fixtures, they will not be rerun.
- Due to xdist plugin limitations, report output will be thrown only when all tests in class are executed. This means that you will not see the output of the failed test until all tests in the class are rerun. Unfortunately, `pytest-xdist` plugin allows reporting results for only scheduled tests in scheduled order. Due to that, tests in class will be grouped by test, but not by rerun, as in regular run.
