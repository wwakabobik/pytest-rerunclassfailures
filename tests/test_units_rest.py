"""This module contains rest of the tests are not covered by the other test modules (mocked tests)"""

from unittest.mock import MagicMock, create_autospec

import pydantic
import pytest
from _pytest.terminal import TerminalReporter

from pytest_rerunclassfailures.pytest_rerunclassfailures import (  # type: ignore
    RerunClassPlugin,
    RerunClassOptions,
    pytest_configure,
)


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


def test_unit_rerun_class_options_accepts_valid_values():
    """Test that RerunClassOptions accepts and stores valid option values"""
    options = RerunClassOptions(rerun_max=2, delay=1.5, only_last=True, hide_terminal_output=False)

    assert options.rerun_max == 2
    assert options.delay == 1.5
    assert options.only_last is True
    assert options.hide_terminal_output is False


@pytest.mark.parametrize("field_name, value", [("rerun_max", -1), ("delay", -0.5)])
def test_unit_rerun_class_options_rejects_negative_values(field_name, value):
    """Test that RerunClassOptions rejects out-of-range (negative) values"""
    kwargs = {"rerun_max": 1, "delay": 0.5, "only_last": False, "hide_terminal_output": False}
    kwargs[field_name] = value

    with pytest.raises(pydantic.ValidationError):
        RerunClassOptions(**kwargs)


def test_unit_plugin_init_rejects_invalid_options():
    """Test that RerunClassPlugin.__init__ turns a pydantic ValidationError into a pytest.UsageError"""
    config = MagicMock()
    config.getoption = MagicMock(side_effect=lambda x: -1 if x == "--rerun-class-max" else 0)

    with pytest.raises(pytest.UsageError, match="pytest-rerunclassfailures: invalid option value"):
        RerunClassPlugin(config=config)


def _make_stacked_setupstate(entries):  # pylint: disable=protected-access
    """
    Build a MagicMock item whose item.session._setupstate.stack behaves like the real
    pytest SetupState.stack: an insertion-ordered dict of node -> (finalizers, exc).

    :param entries: ordered list of (node, finalizers) pairs, root-first
    :type entries: list
    :return: item mock exposing item.session._setupstate.stack
    :rtype: MagicMock
    """
    item = MagicMock()
    item.session._setupstate.stack = {  # pylint: disable=protected-access
        node: (finalizers, None) for node, finalizers in entries
    }
    return item


def test_unit_teardown_class_and_below_pops_only_class_and_function(  # pylint: disable=W0621,protected-access
    rerun_class_plugin,
):
    """Test that only class/function levels are popped and torn down, module/session are kept"""
    session_fin, module_fin, class_fin, function_fin = MagicMock(), MagicMock(), MagicMock(), MagicMock()
    session_node, module_node, class_node, function_node = MagicMock(), MagicMock(), MagicMock(), MagicMock()
    item = _make_stacked_setupstate(
        [
            (session_node, [session_fin]),
            (module_node, [module_fin]),
            (class_node, [class_fin]),
            (function_node, [function_fin]),
        ]
    )
    parent_class = MagicMock()
    parent_class.listchain.return_value = [session_node, module_node, class_node]  # class's own chain, len 3

    rerun_class_plugin._teardown_class_and_below(parent_class, item)  # pylint: disable=protected-access

    class_fin.assert_called_once()
    function_fin.assert_called_once()
    session_fin.assert_not_called()
    module_fin.assert_not_called()
    assert list(item.session._setupstate.stack.keys()) == [
        session_node,
        module_node,
    ]  # pylint: disable=protected-access


def test_unit_teardown_class_and_below_noop_when_already_at_target(rerun_class_plugin):  # pylint: disable=W0621
    """Test that nothing is popped if the stack is already at (or below) the target length"""
    session_fin, module_fin = MagicMock(), MagicMock()
    session_node, module_node = MagicMock(), MagicMock()
    item = _make_stacked_setupstate([(session_node, [session_fin]), (module_node, [module_fin])])
    parent_class = MagicMock()
    parent_class.listchain.return_value = [session_node, module_node, MagicMock()]

    rerun_class_plugin._teardown_class_and_below(parent_class, item)  # pylint: disable=protected-access

    session_fin.assert_not_called()
    module_fin.assert_not_called()


def test_unit_teardown_class_and_below_catches_finalizer_exception(rerun_class_plugin):  # pylint: disable=W0621
    """Test that an exception raised by a finalizer is caught and remaining ones still run"""
    session_fin = MagicMock()
    failing_fin = MagicMock(side_effect=AssertionError("boom"))
    other_fin = MagicMock()
    session_node, module_node, class_node = MagicMock(), MagicMock(), MagicMock()
    item = _make_stacked_setupstate(
        [
            (session_node, [session_fin]),
            (module_node, [module_fin := MagicMock()]),
            (class_node, [other_fin, failing_fin]),
        ]
    )
    parent_class = MagicMock()
    parent_class.listchain.return_value = [session_node, module_node, class_node]

    rerun_class_plugin._teardown_class_and_below(parent_class, item)  # pylint: disable=protected-access

    failing_fin.assert_called_once()
    other_fin.assert_called_once()
    session_fin.assert_not_called()
    module_fin.assert_not_called()


def test_unit_remove_non_initial_attributes_removes_lazily_created_state(rerun_class_plugin):  # pylint: disable=W0621
    """Test that an attribute created after the initial-state snapshot gets removed"""

    class _FakeTestClass:  # pylint: disable=too-few-public-methods
        legit_attr = "should-survive"

    _FakeTestClass.lazily_created = "should-be-removed"
    parent = MagicMock()
    parent.obj = _FakeTestClass
    parent.name = "_FakeTestClass"
    initial_state = {"legit_attr": "should-survive"}

    rerun_class_plugin._remove_non_initial_attributes(parent, initial_state)  # pylint: disable=protected-access

    assert _FakeTestClass.legit_attr == "should-survive"
    assert not hasattr(_FakeTestClass, "lazily_created")


def test_unit_remove_non_initial_attributes_ignores_callables_and_dunders(rerun_class_plugin):  # pylint: disable=W0621
    """Test that methods and dunder/pytestmark attributes are never touched"""

    class _FakeTestClassWithMethod:  # pylint: disable=too-few-public-methods
        def a_method(self):
            """A regular method that must never be removed"""

    parent = MagicMock()
    parent.obj = _FakeTestClassWithMethod
    parent.name = "_FakeTestClassWithMethod"

    rerun_class_plugin._remove_non_initial_attributes(parent, {})  # pylint: disable=protected-access

    assert hasattr(_FakeTestClassWithMethod, "a_method")


def _make_config_mock(rerun_class_max=1, has_rerunfailures=False, allow_rerunfailures=False, warnings_blocked=False):
    options = {
        "--rerun-class-max": rerun_class_max,
        "--rerun-delay": 0.5,
        "--rerun-show-only-last": False,
        "--hide-rerun-details": False,
        "--allow-rerunfailures": allow_rerunfailures,
    }
    config = MagicMock()
    config.getoption = MagicMock(side_effect=lambda name: options[name])
    config.pluginmanager.has_plugin = MagicMock(return_value=has_rerunfailures)
    config.pluginmanager.is_blocked = MagicMock(return_value=warnings_blocked)
    return config


def test_unit_pytest_configure_warns_about_rerunfailures_by_default():
    """Test that pytest_configure warns (but still starts) alongside pytest-rerunfailures"""
    config = _make_config_mock(has_rerunfailures=True)

    pytest_configure(config)

    config.issue_config_time_warning.assert_called_once()
    (warning,), kwargs = config.issue_config_time_warning.call_args
    assert isinstance(warning, pytest.PytestConfigWarning)
    assert "pytest-rerunfailures is also active" in str(warning)
    assert kwargs["stacklevel"] == 2
    config.pluginmanager.register.assert_called_once()


def test_unit_pytest_configure_prints_fallback_when_warnings_blocked(capsys):
    """Test that pytest_configure falls back to a plain print when -p no:warnings is set"""
    config = _make_config_mock(has_rerunfailures=True, warnings_blocked=True)

    pytest_configure(config)

    config.issue_config_time_warning.assert_not_called()
    assert "pytest-rerunfailures is also active" in capsys.readouterr().out
    config.pluginmanager.register.assert_called_once()


def test_unit_pytest_configure_allows_rerunfailures_with_flag():
    """Test that --allow-rerunfailures silences the warning and both plugins coexist"""
    config = _make_config_mock(has_rerunfailures=True, allow_rerunfailures=True)

    pytest_configure(config)

    config.issue_config_time_warning.assert_not_called()
    config.pluginmanager.register.assert_called_once()


def test_unit_pytest_configure_ignores_rerunfailures_check_when_disabled():
    """Test that the rerunfailures check is skipped entirely when this plugin is disabled"""
    config = _make_config_mock(rerun_class_max=0, has_rerunfailures=True)

    pytest_configure(config)

    config.pluginmanager.register.assert_not_called()


def test_unit_pytest_runtest_protocol_defers_non_class_items(rerun_class_plugin):  # pylint: disable=W0621
    """Test that non-class items are deferred (None) rather than handled directly"""
    item = MagicMock()
    item.cls = None

    result = rerun_class_plugin.pytest_runtest_protocol(item, nextitem=MagicMock())

    assert result is None
