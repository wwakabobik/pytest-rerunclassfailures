"""Rerun failed tests in a class to eliminate flaky failures"""

import logging
from copy import deepcopy
from time import sleep
from typing import Tuple

import pytest
import _pytest.nodes
from _pytest.reports import TestReport
from _pytest.runner import runtestprotocol, pytest_runtest_protocol
from _pytest.config.argparsing import Parser


def pytest_addoption(parser: Parser):
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
    """Re-run failed tests in a class"""

    def __init__(self, config: pytest.Config) -> None:
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

    def _report_run(self, item: _pytest.nodes.Item, test_class: dict) -> None:
        """
        Report the class test run.

        :param item: pytest item
        :type item: _pytest.nodes.Item
        :param test_class: test class
        :type test_class: dict
        """
        if item.nodeid in test_class:
            item.ihook.pytest_runtest_logstart(nodeid=item.nodeid, location=item.location)
            for rerun in test_class[item.nodeid]:
                for report in rerun:
                    item.ihook.pytest_runtest_logreport(report=report)
            item.ihook.pytest_runtest_logfinish(nodeid=item.nodeid, location=item.location)
        else:  # if there are no reruns or reruns because fail-fast abort, report the test as skipped
            file, _, test_with_class = item.nodeid.partition("::")
            class_name, _, test_name = test_with_class.partition("::")
            test = f"{class_name}.{test_name}" if class_name and test_name else class_name
            fake_report = TestReport(
                nodeid=item.nodeid,
                location=(file, 0, test),
                keywords={},
                outcome="skipped",
                longrepr=(test, 0, "Skipping test due to class execution was aborted during rerun"),
                when="call",
                sections=[("Reason", "Skipping test due to class execution was aborted during rerun")],
                duration=0.0,
                start=0.0,
                stop=0.0,
                user_properties=[],
            )
            item.ihook.pytest_runtest_logstart(nodeid=item.nodeid, location=item.location)
            item.ihook.pytest_runtest_logreport(report=fake_report)
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
        parent_class = item.getparent(pytest.Class)
        module = item.nodeid.split("::")[0]

        if item.cls is None or self.rerun_max == 0 or not parent_class:  # type: ignore
            pytest_runtest_protocol(item, nextitem=nextitem)
            return False  # ignore non-class items or plugin disabled

        if module not in self.rerun_classes:
            self.rerun_classes[module] = {}
        if parent_class.name not in self.rerun_classes[module]:
            self.rerun_classes[module][parent_class.name] = {}  # to store class run results
        else:
            self._report_run(item, self.rerun_classes[module][parent_class.name])  # report the rest of the results
            return True

        siblings = self._collect_sibling_items(item)

        rerun_count = 0
        passed = False
        initial_state = self._save_parent_initial_state(parent_class)
        while not passed and rerun_count < self.rerun_max:
            passed = True
            for i in range(len(siblings) - 1):
                # Before run, we need to ensure that finalizers are not called (indicated by None in the stack)
                nextitem = siblings[i + 1] if siblings[i + 1] is not None else siblings[0]
                siblings[i].reports = runtestprotocol(siblings[i], nextitem=nextitem, log=False)

                if siblings[i].nodeid not in self.rerun_classes[module][parent_class.name]:
                    self.rerun_classes[module][parent_class.name][siblings[i].nodeid] = []
                while len(self.rerun_classes[module][parent_class.name][siblings[i].nodeid]) <= rerun_count:
                    self.rerun_classes[module][parent_class.name][siblings[i].nodeid].append([])

                for report in siblings[i].reports:
                    self.rerun_classes[module][parent_class.name][siblings[i].nodeid][rerun_count].append(report)
                    if report.failed and not hasattr(report, "wasxfail"):
                        passed = False

                if not passed:
                    rerun_count += 1
                    break  # fail fast

            if not passed and rerun_count < self.rerun_max:
                item, parent_class, siblings = self._teardown_rerun(item, parent_class, siblings, initial_state)
                self.logger.info(
                    "Rerunning %s::%s - %s time(s) after %s seconds", module, parent_class.name, rerun_count, self.delay
                )
                sleep(self.delay)

        self._process_reports(self.rerun_classes[module][parent_class.name])
        self._report_run(item, self.rerun_classes[module][parent_class.name])
        item.session._setupstate.teardown_exact(None)  # pylint: disable=protected-access
        return True

    def _teardown_rerun(
        self, item: _pytest.nodes.Item, parent_class: pytest.Class, siblings: list, initial_state: dict
    ) -> Tuple[_pytest.nodes.Item, pytest.Class, list]:
        """
        Teardown rerun

        :param item: test item under test
        :type item: _pytest.nodes.Item
        :param parent_class: parent class
        :type parent_class: pytest.Class
        :param siblings: siblings of the parent class
        :type siblings: list
        :param initial_state: initial attributes of class
        :type initial_state: dict
        :return: tuple
        """
        # Drop failed fixtures and cache
        self._remove_cached_results_from_failed_fixtures(item)
        # Clean class setup state stack
        item.session._setupstate.stack = {}  # pylint: disable=protected-access
        # Teardown the class and emulate recreation of it
        item.session._setupstate.teardown_exact(None)  # pylint: disable=protected-access
        # We can't replace the class because session-scoped fixtures will be lost
        parent_class, siblings = self._recreate_test_class(parent_class, siblings, initial_state)
        item.parent = parent_class  # ensure that we're using updated class
        return item, parent_class, siblings

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

    def _set_parent_initial_state(self, parent: pytest.Class, state: dict) -> pytest.Class:
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

    def _remove_non_initial_attributes(self, parent: pytest.Class, initial_state: dict) -> None:
        """
        Remove non-initial attributes.

        :param parent: pytest class
        :type parent: pytest.Class
        :param initial_state: parent initial state
        :type initial_state: dict
        """
        for attr_name in dir(parent.obj):
            if (
                not callable(getattr(parent.obj, attr_name))
                and not attr_name.startswith("__")
                and not attr_name.startswith("___")
                and attr_name != "pytestmark"
                and attr_name not in initial_state
            ):
                self.logger.debug("Removing non-default attribute %s from %s", attr_name, parent.name)
                delattr(parent.obj, attr_name)

    def _recreate_test_class(self, test_class: pytest.Class, siblings: list, initial_state: dict) -> tuple:
        """
        Recreate the test class.

        :param test_class: pytest class
        :type test_class: pytest.Class
        :param siblings: list of siblings
        :type siblings: list
        :param initial_state: parent initial state
        :type initial_state: dict
        :return: test_class and siblings
        :rtype: tuple
        """
        # Drop a previous failed flag only when we are going to rerun the test
        if hasattr(test_class, "_previousfailed"):
            delattr(test_class, "_previousfailed")

        # Remove non-initial attributes. BUT! currently we can't remove them because we're not re-call the fixtures
        #  self._remove_non_initial_attributes(test_class, initial_state)
        # Load the original test class from the pytest Class object and propagate to the siblings
        self._set_parent_initial_state(test_class, initial_state)
        for i in range(len(siblings) - 1):
            siblings[i].parent = test_class

        return test_class, siblings

    def _process_reports(self, test_class: dict) -> None:
        """
        Process the reports.

        :param class_name: class name
        :type class_name: dict
        :return: None
        :rtype: None
        """
        for sibling, reruns in test_class.items():
            if len(reruns) > 1:
                if self.only_last:
                    test_class[sibling] = [reruns[-1]]
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
                        _, _, err = getattr(fixture_def, cached_result)
                        if err:  # Deleting cached results for only failed fixtures
                            self.logger.debug("Removing cached result for %s", fixture_def)
                            setattr(fixture_def, cached_result, None)


def pytest_configure(config: pytest.Config):
    """
    Configure the plugin.

    :param config: pytest config
    :type config: pytest.Config
    """
    if config.getoption("--rerun-class-max") > 0:
        rerun_plugin = RerunClassPlugin(config)
        config.pluginmanager.register(rerun_plugin, "pytest-rerunclassfailures")
