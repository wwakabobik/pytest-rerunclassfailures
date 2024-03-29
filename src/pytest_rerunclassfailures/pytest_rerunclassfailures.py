"""Rerun failed tests in a class to eliminate flaky failures"""

import logging
from copy import deepcopy
from time import sleep
from typing import Tuple, Literal, Union

import pytest
import _pytest.nodes
from _pytest.terminal import TerminalReporter
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.reports import TestReport
from _pytest.runner import runtestprotocol, pytest_runtest_protocol
from _pytest._code.code import ExceptionInfo, TerminalRepr  # pylint: disable=protected-access


def pytest_addoption(parser: Parser) -> None:
    """
    Add options to the parser.

    :param parser: pytest parser
    :type parser: _pytest.config.argparsing.Parser
    :return: None
    :rtype: None
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
        help="show only the last rerun if passed",
    )
    group.addoption(
        "--hide-rerun-details",
        action="store_true",
        dest="hide_rerun_details",
        default=False,
        help="hide rerun details in terminal output if passed",
    )


class RerunClassPlugin:  # pylint: disable=too-few-public-methods
    """Re-run failed tests in a class"""

    def __init__(self, config: pytest.Config) -> None:
        """
        Initialize RerunClassPlugin class.

        :param config: pytest config
        :type config: _pytest.config.Config
        :return: None
        :rtype: None
        """
        self.rerun_classes: dict = {}  # test classed already rerun
        self.rerun_max = config.getoption("--rerun-class-max")  # how many times to rerun the class
        self.rerun_max = self.rerun_max + 1 if self.rerun_max > 0 else 0  # increment by 1 to include the initial run
        self.delay = config.getoption("--rerun-delay")  # delay between reruns in seconds
        self.only_last = config.getoption("--rerun-show-only-last")  # rerun only the last failed test
        self.hide_terminal_output = config.getoption("--hide-rerun-details")  # hide rerun details in terminal output
        self.logger = logging.getLogger("pytest")
        self.logger.debug("pytest-rerunclassfailures plugin initialized!")

    @staticmethod
    def _generate_fake_report(
        nodeid: str,
        longrepr: Union[None, ExceptionInfo[BaseException], Tuple[str, int, str], str, TerminalRepr],
        sections: list,
        location: tuple,
        outcome: Literal["passed", "failed", "skipped", "rerun", "error", "xfailed", "xpassed"],
    ) -> TestReport:
        """
        Generate a fake report for the skipped or error test.
        :param nodeid: node id
        :type nodeid: str
        :param longrepr: longrepr
        :type longrepr: Union[None, ExceptionInfo[BaseException], Tuple[str, int, str], str, TerminalRepr]
        :param sections: sections
        :type sections: list
        :param location: location
        :type location: tuple
        :param outcome: outcome
        :type outcome: Literal["passed", "failed", "skipped", "rerun", "error", "xfailed", "xpassed"]
        :return: fake report
        :rtype: TestReport
        """
        fake_report = TestReport(
            nodeid=nodeid,
            location=location,
            keywords={},
            outcome=outcome,  # type: ignore
            longrepr=longrepr,
            when="call",
            sections=sections,
            duration=0.0,
            start=0.0,
            stop=0.0,
            user_properties=[],
        )
        return fake_report

    def _report_run(self, item: _pytest.nodes.Item, test_class: dict) -> None:
        """
        Report the class test run.

        :param item: pytest item
        :type item: _pytest.nodes.Item
        :param test_class: test class with tests node ids
        :type test_class: dict
        :return: None
        :rtype: None
        """
        self.logger.debug("Reporting node results %s", item.nodeid)
        if item.nodeid in test_class:
            item.ihook.pytest_runtest_logstart(nodeid=item.nodeid, location=item.location)
            for index, rerun in enumerate(test_class[item.nodeid]):
                self.logger.debug("Reporting node results %s (%s/%s)", item.nodeid, len(test_class[item.nodeid]), index)
                for report in rerun:
                    item.ihook.pytest_runtest_logreport(report=report)
            item.ihook.pytest_runtest_logfinish(nodeid=item.nodeid, location=item.location)
        else:  # if there are no reruns or reruns because fail-fast abort, report the test as skipped
            file, _, test_with_class = item.nodeid.partition("::")
            class_name, _, test_name = test_with_class.partition("::")
            test = f"{class_name}.{test_name}" if class_name and test_name else class_name
            longrepr = (test, 0, "Skipping test due to class execution was aborted during rerun")
            sections = [("Reason", "Skipping test due to class execution was aborted during rerun")]
            location = (file, 0, test)
            fake_report = self._generate_fake_report(item.nodeid, longrepr, sections, location, "skipped")
            self.logger.debug("Reporting test node was skipped %s", item.nodeid)
            item.ihook.pytest_runtest_logstart(nodeid=item.nodeid, location=item.location)
            item.ihook.pytest_runtest_logreport(report=fake_report)
            item.ihook.pytest_runtest_logfinish(nodeid=item.nodeid, location=item.location)

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_protocol(
        self, item: _pytest.nodes.Item, nextitem: _pytest.nodes.Item  # pylint: disable=W0613
    ) -> bool:
        """
        Run the test protocol.

        :param item: pytest item
        :type item: _pytest.nodes.Item
        :param nextitem: next pytest item
        :type nextitem: _pytest.nodes.Item
        :return: True if any actions of plugin performed, False otherwise
        :rtype: bool
        """
        parent_class = item.getparent(pytest.Class)
        module = item.nodeid.split("::")[0]

        if item.cls is None or self.rerun_max <= 0 or not parent_class:  # type: ignore
            self.logger.debug("Ignoring %s (node have no parent class)", item.nodeid)
            pytest_runtest_protocol(item, nextitem=nextitem)
            return False  # ignore non-class items or plugin disabled

        if module not in self.rerun_classes:
            self.rerun_classes[module] = {}
        if parent_class.name not in self.rerun_classes[module]:
            self.rerun_classes[module][parent_class.name] = {}  # to store class run results
        else:
            self.logger.debug(
                "Node %s was already executed for % class, reporting rest", item.nodeid, parent_class.name
            )
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
        self._teardown_test_class(item)
        return True

    def _teardown_test_class(self, item: _pytest.nodes.Item) -> None:
        """
        Teardown the test class.

        :param item: pytest item
        :type item: _pytest.nodes.Item
        :return: None
        :rtype: None
        """
        self.logger.debug("Teardown test class %s", item.nodeid)
        try:
            item.session._setupstate.teardown_exact(None)  # pylint: disable=protected-access
        except Exception as error:  # pylint: disable=broad-except
            self.logger.warning("\nException during teardown: %s: %s", type(error).__name__, error)

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
        self._teardown_test_class(item)  # Teardown the class and emulate recreation of it
        # We can't replace the class because session-scoped fixtures will be lost
        parent_class, siblings = self._recreate_test_class(parent_class, siblings, initial_state)
        item.parent = parent_class  # ensure that we're using updated class
        return item, parent_class, siblings

    def _collect_sibling_items(self, item: _pytest.nodes.Item) -> list:
        """
        Collect sibling items.

        :param item: current pytest item
        :type item: _pytest.nodes.Item
        :return: sibling items
        :rtype: list
        """
        self.logger.debug("Collecting siblings for %s", item.nodeid)
        siblings = [item]
        items = item.session.items

        for i in items[items.index(item) + 1 :]:
            if item.cls == i.cls:  # type: ignore
                siblings.append(i)
        siblings.append(None)  # type: ignore
        self.logger.debug("Collected siblings: %s", len(siblings) - 1)

        return siblings

    def _save_parent_initial_state(self, parent: pytest.Class) -> dict:
        """
        Save the parent initial state.

        :param parent: pytest item
        :type parent: _pytest.Item
        :return: parent initial state
        :rtype: dict
        """
        self.logger.debug("Saving state of parent class %s", parent.name)
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
        self.logger.debug("Loading state of parent class %s", parent.name)
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

        TBD: Currently, we can't remove them because we're not re-call the fixtures.

        :param parent: pytest class
        :type parent: pytest.Class
        :param initial_state: parent initial state
        :type initial_state: dict
        :return: None
        :rtype: None
        """
        self.logger.debug("Removing non-default attributes from %s", parent.name)  # pragma: no cover
        for attr_name in dir(parent.obj):  # pragma: no cover
            if (  # pragma: no cover
                not callable(getattr(parent.obj, attr_name))
                and not attr_name.startswith("__")
                and not attr_name.startswith("___")
                and attr_name != "pytestmark"
                and attr_name not in initial_state
            ):
                self.logger.debug(  # pragma: no cover
                    "Removing non-default attribute %s from %s", attr_name, parent.name
                )
                delattr(parent.obj, attr_name)  # pragma: no cover

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
        self.logger.debug("Recreating class %s", test_class.name)
        # Drop a previous failed flag only when we are going to rerun the test, actually should never happen
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

        :param test_class: dict with test class test results (including reruns)
        :type test_class: dict
        :return: None
        :rtype: None
        """
        self.logger.debug("Preparing reports before publication")
        for sibling, reruns in test_class.items():
            if len(reruns) > 1:
                if self.only_last:
                    test_class[sibling] = [reruns[-1]]
                else:
                    for rerun in reruns[:-1]:
                        for report in rerun:
                            dummy_report = self._check_and_add_dummy_rerun_if_needed(report)
                            rerun.append(dummy_report) if dummy_report else None  # pylint: disable=W0106
                            report.outcome = "rerun"

    def _check_and_add_dummy_rerun_if_needed(self, report: TestReport) -> Union[None, TestReport]:
        """
        Check and add a dummy rerun report if needed.

        :param report: test report
        :type report: TestReport
        :return: None or TestReport
        :rtype: Union[None, TestReport]
        """
        if report.outcome == "failed" and report.when == "setup":
            return self._generate_fake_report(report.nodeid, report.longrepr, report.sections, report.location, "rerun")
        return None

    def _remove_cached_results_from_failed_fixtures(self, item: _pytest.nodes.Item) -> None:
        """
        Remove all cached_result attributes from every fixture.

        :param item: pytest item
        :type item: _pytest.nodes.Item
        :return: None
        :rtype: None
        """
        self.logger.debug("Removing cached results from failed fixtures")
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

    def pytest_terminal_summary(
        self, terminalreporter: TerminalReporter, exitstatus: int, config: Config  # pylint: disable=unused-argument
    ) -> None:
        """
        Reports reruns section to terminal.

        :param terminalreporter: pytest terminal reporter
        :type terminalreporter: _pytest.terminal.TerminalReporter
        :param exitstatus: exit status
        :type exitstatus: int
        :param config: pytest config
        :type config: _pytest.config.Config
        :return: None
        :rtype: None
        """
        if "rerun" not in terminalreporter.stats or self.hide_terminal_output:
            self.logger.debug("Skipping passing reruns section to terminal, because no reruns or hiding rerun details")
            return

        self.logger.debug("Passing reruns section to terminal")
        terminalreporter._tw.sep("=", "RERUNS")  # pylint: disable=W0212

        for rerun_test in terminalreporter.stats["rerun"]:
            pos = rerun_test.nodeid
            terminalreporter._tw.line(f"RERUN {pos}")  # pylint: disable=W0212

            if hasattr(rerun_test, "longrepr"):
                if isinstance(rerun_test.longrepr, tuple):
                    for line in rerun_test.longrepr:
                        if line:
                            terminalreporter._tw.line(str(line))  # pylint: disable=W0212
                else:
                    if rerun_test.longrepr:
                        terminalreporter._tw.line(str(rerun_test.longrepr))  # pylint: disable=W0212


def pytest_configure(config: Config) -> None:
    """
    Configure the plugin.

    :param config: pytest config
    :type config: pytest.Config
    :return: None
    :rtype: None
    """
    if config.getoption("--rerun-class-max") > 0:
        rerun_plugin = RerunClassPlugin(config)
        config.pluginmanager.register(rerun_plugin, "pytest-rerunclassfailures")
