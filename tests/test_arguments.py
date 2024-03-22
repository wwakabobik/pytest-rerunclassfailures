"""Test against the different command-line arguments passed to the plugin."""

from os import environ
from random import randint, choice
from re import findall
from subprocess import check_output, STDOUT, CalledProcessError

import pytest

from .type_check import FixtureRequest


@pytest.fixture
def run_tests_with_plugin(request: FixtureRequest):  # pylint: disable=unused-argument
    """
    Fixture to run pytest with the plugin.

    :param request: pytest request object
    :type request: _pytest.fixtures.FixtureRequest
    :return: function to run pytest with the plugin
    :rtype: function
    """

    def run(test_path: str, args: list) -> tuple:
        """
        Run pytest with the plugin and arguments.

        :param test_path: path to the test file
        :type test_path: str
        :param args: list of arguments to pass to pytest (actually to the plugin)
        :type args: list[str]
        :return: tuple with the return code and the output
        :rtype: tuple
        """
        return_code = 0
        try:
            env = environ.copy()
            env["PYTHONPATH"] = "./src/pytest_rerunclassfailures"
            output = check_output(
                ["pytest", test_path, "-p", "pytest_rerunclassfailures"] + args,
                text=True,
                stderr=STDOUT,
                env=env,
            )
        except CalledProcessError as exc:
            output = exc.output
            return_code = exc.returncode

        return return_code, output

    return run


@pytest.fixture(params=[[], ["--rerun-class-max=0"]], ids=["no_arguments", "zero reruns"])
def plugin_disabled(request: FixtureRequest, run_tests_with_plugin) -> tuple:  # pylint: disable=W0621
    """
    Fixture to run pytest with disabled plugin.

    :param request: pytest request object
    :type request: _pytest.fixtures.FixtureRequest
    :param run_tests_with_plugin: fixture to run pytest with the plugin
    :type run_tests_with_plugin: function
    :return: tuple with the return code and the output
    :rtype: tuple
    """
    return run_tests_with_plugin("tests/test_source/test_basic.py", request.param)


@pytest.fixture(params=[1, randint(2, 10)], ids=["one_rerun", "several_reruns"])
def plugin_enabled(request: FixtureRequest, run_tests_with_plugin) -> tuple:  # pylint: disable=W0621
    """
    Fixture to run pytest with enabled plugin with different rerun count values.

    :param request: pytest request object
    :type request: _pytest.fixtures.FixtureRequest
    :param run_tests_with_plugin: fixture to run pytest with the plugin
    :type run_tests_with_plugin: function
    :return: tuple with the return code and the output
    :rtype: tuple
    """
    arg = "--rerun-class-max=" + str(request.param)
    return run_tests_with_plugin("tests/test_source/test_always_fails.py", [arg]), request.param


@pytest.fixture(params=[None, 0, float(randint(5, 100)) / 10.0], ids=["default", "zero_delay", "several_seconds"])
def plugin_delay(request: FixtureRequest, run_tests_with_plugin) -> tuple:  # pylint: disable=W0621
    """
    Fixture to run pytest with plugin with different delay values.

    :param request: pytest request object
    :type request: _pytest.fixtures.FixtureRequest
    :param run_tests_with_plugin: fixture to run pytest with the plugin
    :type run_tests_with_plugin: function
    :return: tuple with the return code and the output
    :rtype: tuple
    """
    args = ["--rerun-class-max=1"]
    if request.param is not None:
        args += ["--rerun-delay=" + str(request.param)]
    return run_tests_with_plugin("tests/test_source/test_always_fails.py", args), request.param


@pytest.fixture(
    params=[
        f"--rerun-class-max={choice((True, None, '', 'abc'))}",
        f"--rerun-show-only-last={choice((True, 0.5, None, '', 'abc'))}",
        f"--rerun-delay={choice((True, None, '', 'abc'))}",
    ],
    ids=["incorrect", "show_only_last", "delay"],
)
def plugin_invalid_arguments(request: FixtureRequest, run_tests_with_plugin) -> tuple:  # pylint: disable=W0621
    """
    Fixture to run pytest with enabled plugin with different rerun count values.

    :param request: pytest request object
    :type request: _pytest.fixtures.FixtureRequest
    :param run_tests_with_plugin: fixture to run pytest with the plugin
    :type run_tests_with_plugin: function
    :return: tuple with the return code and the output
    :rtype: tuple
    """
    arg_rerun = [f"--rerun-class-max={randint(1, 10)}"]
    arg = arg_rerun + [str(request.param)] if "--rerun-show-only-last" not in request.param else [str(request.param)]
    return run_tests_with_plugin("tests/test_source/test_always_fails.py", arg), request.param.split("=")[0]


def test_arguments_plugin_disabled(plugin_disabled):  # pylint: disable=W0621
    """
    Test that the plugin is disabled when no arguments are passed.

    :param plugin_disabled: fixture to run pytest with disabled plugin
    :type plugin_disabled: function
    :return: none
    """
    error_code, output = plugin_disabled
    assert error_code == 1
    assert "tests/test_source/test_basic.py::TestBasic::test_basic PASSED" in output
    assert "tests/test_source/test_basic.py::TestBasic::test_basic2 FAILED" in output
    assert "tests/test_source/test_basic.py::TestBasic::test_basic3 PASSED" in output
    assert " 1 failed, 2 passed in " in output


def test_arguments_rerun_count(plugin_enabled):  # pylint: disable=W0621
    """
    Test that the plugin reruns the test the correct number of times.

    :param plugin_enabled: fixture to run pytest with enabled plugin
    :type plugin_enabled: function
    :return: none
    """
    (error_code, output), rerun_count = plugin_enabled
    assert error_code == 1
    assert "tests/test_source/test_always_fails.py::TestAlwaysFail::test_always_fail FAILED" in output
    assert output.count("tests/test_source/test_always_fails.py::TestAlwaysFail::test_always_fail RERUN") == rerun_count
    assert f"1 failed, {rerun_count} rerun in " in output


def test_arguments_delay(plugin_delay):  # pylint: disable=W0621
    """
    Test that the plugin delays the rerun the correct number of seconds.

    :param plugin_delay: fixture to run pytest with enabled plugin
    :type plugin_delay: function
    :return: none
    """
    (error_code, output), delay = plugin_delay
    run_time = findall(r"(1 failed, 1 rerun in )(\d+\.\d+)(s)", output)[0][1]

    if delay is None:
        delay = 0.5
    assert error_code == 1
    assert float(run_time) >= delay


def test_arguments_show_only_last(run_tests_with_plugin):  # pylint: disable=W0621
    """
    Test that the plugin only shows the last run when the argument is passed.

    :param run_tests_with_plugin: fixture to run pytest with the plugin
    :type run_tests_with_plugin: function
    :return: none
    """
    args = ["--rerun-class-max=1", "--rerun-show-only-last"]
    error_code, output = run_tests_with_plugin("tests/test_source/test_always_fails.py", args)
    assert error_code == 1
    assert "tests/test_source/test_always_fails.py::TestAlwaysFail::test_always_fail FAILED" in output
    assert "tests/test_source/test_always_fails.py::TestAlwaysFail::test_always_fail RERUN" not in output
    assert "1 failed in " in output


def test_arguments_invalid_arguments(plugin_invalid_arguments):  # pylint: disable=W0621
    """
    Test that the plugin returns an error when invalid arguments are passed.

    :param plugin_invalid_arguments: fixture to run pytest with the plugin
    :type plugin_invalid_arguments: function
    :return: none
    """
    (error_code, output), param = plugin_invalid_arguments
    assert f"error: argument {param}" in output
    assert error_code == 4
