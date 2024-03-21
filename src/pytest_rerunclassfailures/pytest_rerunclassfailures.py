"""Rerun failed tests in a class to eliminate flaky failures."""

import logging
from copy import deepcopy
from time import sleep
from typing import Optional

import _pytest.nodes
import pytest
from _pytest.runner import runtestprotocol


def pytest_addoption(parser):
    """
    Add options to the parser.

    :param parser: pytest parser
    :type parser: _pytest.config.argparsing.Parser
    """
    group = parser.getgroup("rerunclassfailures", "rerun class failures to eliminate flaky failures")
    group.addoption(
        "--rerun-class-max", action="store", default=0, type=int, help="maximum number of times to rerun a test class"
    )
    group.addoption(
        "--rerun-delay",
        action="store",
        dest="rerun_delay",
        type=float,
        default=0.5,
        help="add time (seconds) delay between reruns",
    )
    group.addoption(
        "--rerun-show-only-last",
        action="store_true",
        dest="rerun_show_only_last",
        default=False,
        help="show only the last rerun if True, otherwise show all tries",
    )


class RerunClassPlugin:  # pylint: disable=too-few-public-methods
    """Re-run failed tests in a class."""

    def __init__(self, config) -> None:
        """
        Initialize RerunClassPlugin class.

        :param config: pytest config
        :type config: _pytest.config.Config
        """
        self.rerun_classes: dict = {}  # test classed already rerun
        self.rerun_max = config.getoption("--rerun-class-max")  # how many times to rerun the class
        self.rerun_max = self.rerun_max + 1 if self.rerun_max > 0 else 0  # increment by 1 to include the initial run
        self.delay = config.getoption("--rerun-delay")  # delay between reruns in seconds
        self.only_last = config.getoption("--rerun-show-only-last")  # rerun only the last failed test
        self.logger = logging.getLogger("pytest")

    def _report_run(self, item: _pytest.nodes.Item, cls_name: str) -> None:
        """
        Report the class test run.

        :param item: pytest item
        :type item: _pytest.nodes.Item
        """
        if cls_name in self.rerun_classes:
            if item.nodeid in self.rerun_classes[cls_name]:
                item.ihook.pytest_runtest_logstart(nodeid=item.nodeid, location=item.location)
                for rerun in self.rerun_classes[cls_name][item.nodeid]:
                    for report in rerun:
                        item.ihook.pytest_runtest_logreport(report=report)
                item.ihook.pytest_runtest_logfinish(nodeid=item.nodeid, location=item.location)

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_protocol(self, item: _pytest.nodes.Item, nextitem: _pytest.nodes.Item):  # pylint: disable=W0613
        """
        Run the test protocol.

        :param item: pytest item
        :type item: _pytest.nodes.Item
        :param nextitem: next pytest item
        :type nextitem: _pytest.nodes.Item
        """
        if item.cls is None or self.rerun_max == 0:  # type: ignore
            return False  # ignore non-class items or plugin disabled

        cls = item.getparent(pytest.Class)
        cls_name = cls.name  # type: ignore
        initial_state = self._save_parent_initial_state(cls)

        if cls_name not in self.rerun_classes:
            self.rerun_classes[cls_name] = {}  # to store class run results
        else:
            self._report_run(item, cls_name)  # report the rest of the results we already made in scheduled time
            return False

        siblings = self._collect_sibling_items(item)

        rerun_count = 0
        passed = False
        while not passed and rerun_count < self.rerun_max:
            passed = True
            for i in range(len(siblings) - 1):
                # Before run, we need to ensure that finalizers are not called (indicated by None in the stack)
                nextitem = siblings[i + 1] if siblings[i + 1] is not None else siblings[0]
                siblings[i].reports = runtestprotocol(siblings[i], nextitem=nextitem, log=False)

                # Create a new list of reports for each rerun, if needed
                if siblings[i].nodeid not in self.rerun_classes[cls_name]:
                    self.rerun_classes[cls_name][siblings[i].nodeid] = []
                if rerun_count not in self.rerun_classes[cls_name][siblings[i].nodeid]:
                    self.rerun_classes[cls_name][siblings[i].nodeid].append([])

                for report in siblings[i].reports:
                    self.rerun_classes[cls_name][siblings[i].nodeid][rerun_count].append(report)
                    if report.failed and not hasattr(report, "wasxfail"):
                        passed = False

                if not passed:
                    rerun_count += 1
                    break  # fail fast

            if not passed and rerun_count < self.rerun_max:
                item, cls, siblings = self._teardown_rerun(item, cls, siblings, initial_state)
                self.logger.info("Rerunning %s - %s time(s) after %s seconds", cls_name, rerun_count, self.delay)
                sleep(self.delay)

        self._process_reports(cls_name)
        self._report_run(item, cls_name)
        item.session._setupstate.teardown_exact(None)  # pylint: disable=protected-access
        return True

    def _teardown_rerun(
        self, item: _pytest.nodes.Item, cls: Optional[pytest.Class], siblings: list, initial_state: dict
    ) -> tuple:
        """
        Teardown rerun

        :param item:
        :param cls:
        :param siblings:
        :param initial_state:
        :return:
        """
        # Drop failed fixtures and cache
        self._remove_cached_results_from_failed_fixtures(item)
        # Clean class setup state stack
        item.session._setupstate.stack = {}  # pylint: disable=protected-access
        # Teardown the class and emulate recreation of it
        item.session._setupstate.teardown_exact(None)  # pylint: disable=protected-access
        # We can't replace the class because session-scoped fixtures will be lost
        cls, siblings = self._recreate_test_class(cls, siblings, initial_state)
        item.parent = cls  # ensure that we're using updated class
        return item, cls, siblings

    @staticmethod
    def _collect_sibling_items(item: _pytest.nodes.Item) -> list:
        """
        Collect sibling items.

        :param item: current pytest item
        :type item: _pytest.nodes.Item
        :return: sibling items
        :rtype: list
        """
        siblings = [item]
        items = item.session.items

        for i in items[items.index(item) + 1 :]:
            if item.cls == i.cls:  # type: ignore
                siblings.append(i)
        siblings.append(None)  # type: ignore

        return siblings

    def _save_parent_initial_state(self, parent):
        """
        Save the parent initial state.

        :param parent: pytest item
        :type parent: _pytest.
        :return: parent initial state
        :rtype: dict
        """
        obj = parent.obj
        attrs = {}
        for attr_name in dir(obj):
            if (
                not callable(getattr(obj, attr_name))
                and not attr_name.startswith("__")
                and not attr_name.startswith("___")
                and attr_name != "pytestmark"
            ):
                attr_value = getattr(obj, attr_name)
                try:
                    attrs[attr_name] = deepcopy(attr_value)
                except Exception as error:  # pylint: disable=broad-except
                    # sometimes we can't deepcopy, in this case, store the value
                    attrs[attr_name] = attr_value  # sometimes we can't deepcopy, in this case, create a link
                    self.logger.debug("While saving state of parent class: can't deepcopy %s: %s", attr_name, error)
        return attrs

    def _set_parent_initial_state(self, parent: Optional[pytest.Class], state: dict) -> pytest.Class:
        """
        Set the parent initial state.

        :param parent: pytest class
        :type parent: pytest.Class
        :param state: parent initial state
        :type state: dict
        """
        for attr_name, attr_value in state.items():
            try:
                setattr(parent.obj, attr_name, deepcopy(attr_value))
            except Exception as error:  # pylint: disable=broad-except
                # sometimes we can't deepcopy, in this case, store the value
                setattr(parent.obj, attr_name, attr_value)
                self.logger.debug("While loading state of parent class: can't deepcopy %s: %s", attr_name, error)
        return parent

    def _recreate_test_class(self, cls: Optional[pytest.Class], siblings: list, initial_state: dict) -> tuple:
        """
        Recreate the test class.

        :param cls: pytest class
        :type cls: pytest.Class
        :param siblings: list of siblings
        :type siblings: list
        :param initial_state: parent initial state
        :type initial_state: dict
        :return: cls and siblings
        :rtype: tuple
        """
        # Drop a previous failed flag only when we are going to rerun the test
        if hasattr(cls, "_previousfailed"):
            delattr(cls, "_previousfailed")

        # Load the original test class from the pytest Class object and propagate to the siblings
        self._set_parent_initial_state(cls, initial_state)
        for i in range(len(siblings) - 1):
            siblings[i].parent = cls

        return cls, siblings

    def _process_reports(self, cls_name) -> None:
        """
        Process the reports.

        :param cls_name: class name
        :type cls_name: str
        :return: None
        :rtype: None
        """
        for sibling, reruns in self.rerun_classes[cls_name].items():
            if len(reruns) > 1:
                if self.only_last:
                    self.rerun_classes[cls_name][sibling] = [reruns[-1]]
                else:
                    for rerun in reruns[:-1]:
                        for report in rerun:
                            report.outcome = "rerun"

    def _remove_cached_results_from_failed_fixtures(self, item: _pytest.nodes.Item) -> None:
        """
        Remove all cached_result attributes from every fixture.

        :param item: pytest item
        :type item: _pytest.nodes.Item
        """
        cached_result = "cached_result"
        fixture_info = getattr(item, "_fixtureinfo", None)
        if fixture_info:
            for fixture_def_str in getattr(fixture_info, "name2fixturedefs", ()):
                fixture_defs = fixture_info.name2fixturedefs[fixture_def_str]
                for fixture_def in fixture_defs:
                    if getattr(fixture_def, cached_result, None) is not None:
                        result, _, err = getattr(fixture_def, cached_result)
                        if err:  # Deleting cached results for only failed fixtures
                            setattr(fixture_def, result, None)


def pytest_configure(config):
    """
    Configure the plugin.

    :param config: pytest config
    :type config: _pytest.config.Config
    """
    if config.getoption("--rerun-class-max") > 0:
        rerun_plugin = RerunClassPlugin(config)
        config.pluginmanager.register(rerun_plugin, "rerun_class_plugin")
