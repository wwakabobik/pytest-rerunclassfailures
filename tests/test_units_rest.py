"""This module contains rest of the tests are not covered by the other test modules (mocked tests)"""

from unittest.mock import MagicMock, create_autospec

import pytest
from _pytest.terminal import TerminalReporter

from pytest_rerunclassfailures.pytest_rerunclassfailures import RerunClassPlugin  # type: ignore


@pytest.fixture
def mock_pytest_config() -> MagicMock:
    """
    Fixture for creating a mock of pytest.Config

    :return: mock of pytest.Config
    :rtype: MagicMock
    """
    config = MagicMock()
    config.getoption = MagicMock(side_effect=lambda x: 1 if x == "--rerun-class-max" else 0)
    return config


@pytest.fixture
def rerun_class_plugin(mock_pytest_config: MagicMock) -> RerunClassPlugin:  # pylint: disable=W0621
    """
    Fixture for creating an instance of RerunClassPlugin

    :param mock_pytest_config: mock of pytest.Config
    :type mock_pytest_config: MagicMock
    :return: instance of RerunClassPlugin
    :rtype: RerunClassPlugin
    """
    plugin = RerunClassPlugin(config=mock_pytest_config)
    plugin.hide_terminal_output = False
    plugin.logger = MagicMock()
    return plugin


def test_unit_previousfailed_removed_at_teardown(rerun_class_plugin):  # pylint: disable=W0621
    """
    Test that the _previousfailed attribute is removed from the test class

    :param rerun_class_plugin: instance of RerunClassPlugin
    :type rerun_class_plugin: RerunClassPlugin
    :return: None
    :rtype: None
    """
    test_class_mock = create_autospec(pytest.Class, instance=True)
    setattr(test_class_mock, "_previousfailed", True)

    siblings_mock = [MagicMock() for _ in range(3)]
    initial_state_mock = {}

    result_test_class, result_siblings = rerun_class_plugin._recreate_test_class(  # pylint: disable=protected-access
        test_class=test_class_mock, siblings=siblings_mock, initial_state=initial_state_mock
    )

    assert not hasattr(result_test_class, "_previousfailed"), "The _previousfailed attribute should be removed"
    assert result_test_class is test_class_mock, "The test_class should be returned as is"
    assert result_siblings is siblings_mock, "The siblings should be returned as is"


def test_unit_pytest_terminal_summary_with_tuple(rerun_class_plugin, mock_pytest_config):  # pylint: disable=W0621
    """
    Test that the pytest_terminal_summary method works correctly with tuple longrepr

    :param rerun_class_plugin: instance of RerunClassPlugin
    :type rerun_class_plugin: RerunClassPlugin
    :return: None
    :rtype: None
    """
    terminalreporter = create_autospec(TerminalReporter, instance=True)
    terminalreporter.stats = {"rerun": [MagicMock()]}
    terminalreporter._tw = MagicMock()  # pylint: disable=protected-access

    rerun_test = terminalreporter.stats["rerun"][0]
    rerun_test.nodeid = "test_nodeid"
    rerun_test.longrepr = ("line1", "line2", "line3")

    rerun_class_plugin.pytest_terminal_summary(terminalreporter, exitstatus=0, config=mock_pytest_config)

    assert terminalreporter._tw.line.call_count == 4  # pylint: disable=protected-access
    terminalreporter._tw.line.assert_any_call("RERUN test_nodeid")  # pylint: disable=protected-access
    terminalreporter._tw.line.assert_any_call("line1")  # pylint: disable=protected-access
    terminalreporter._tw.line.assert_any_call("line2")  # pylint: disable=protected-access
    terminalreporter._tw.line.assert_any_call("line3")  # pylint: disable=protected-access
