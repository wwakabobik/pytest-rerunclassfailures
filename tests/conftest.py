"""Test against the different command-line arguments passed to the plugin."""

from os import environ
from subprocess import check_output, STDOUT, CalledProcessError
from typing import Optional, Union

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

    def run(test_path: Union[str, list], args: list) -> tuple:
        """
        Run pytest with the plugin and arguments.

        :param test_path: path to the test file or list of paths
        :type test_path: Union[str, list]
        :param args: list of arguments to pass to pytest (actually to the plugin)
        :type args: list[str]
        :return: tuple with the return code and the output
        :rtype: tuple
        """
        print(f"Running pytest with the plugin and arguments: {args}")
        return_code = 0
        test_path = test_path.split(" ") if isinstance(test_path, str) else test_path
        try:
            env = environ.copy()
            env["PYTHONPATH"] = "./src/pytest_rerunclassfailures"
            output = check_output(
                ["pytest"] + test_path + ["-p", "pytest_rerunclassfailures"] + args,
                text=True,
                stderr=STDOUT,
                env=env,
            )
        except CalledProcessError as exc:
            output = exc.output
            return_code = exc.returncode

        return return_code, output

    return run


@pytest.fixture
def run_default_tests(run_tests_with_plugin):  # pylint: disable=redefined-outer-name
    """
    Fixture to run pytest with the plugin and default arguments.

    :param run_tests_with_plugin: fixture to run pytest with the plugin
    :type run_tests_with_plugin: function
    :return: function to run pytest with the plugin and default arguments
    :rtype: function
    """

    def run(test_path: str, args: Optional[str] = None) -> tuple:
        """
        Run pytest with the plugin and arguments.

        :param test_path: path to the test file
        :type test_path: str
        :param args: list of arguments to pass to pytest (actually to the plugin)
        :type args: list[str]
        :return: tuple with the return code and the output
        :rtype: tuple
        """
        arg_list = ["--rerun-class-max=1"]
        if args:
            arg_list += args.split(" ")
        return run_tests_with_plugin(test_path, arg_list)

    return run
