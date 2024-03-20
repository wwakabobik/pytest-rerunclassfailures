"""Rerun failed tests in a class to eliminate flaky failures."""

from copy import deepcopy
from time import sleep

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
        action="store",
        dest="rerun_show_only_last",
        type=bool,
        default=False,
        help="show only the last rerun if True, otherwise show all tries",
    )


class RerunClassPlugin:
    """Re-run failed tests in a class."""

    def __init__(self, config):
        """
        Initialize RerunClassPlugin class.

        :param config: pytest config
        :type config: _pytest.config.Config
        """
        self.rerun_classes = []  # test classed already rerun
        self.rerun_max = config.getoption("--rerun-class-max")  # how many times to rerun the class
        self.rerun_max = self.rerun_max + 1 if self.rerun_max > 0 else 0  # increment by 1 to include the initial run
        self.delay = config.getoption("--rerun-delay")  # delay between reruns in seconds
        self.only_last = config.getoption("--rerun-show-only-last")  # rerun only the last failed test

    def _report_run(self, item):
        """
        Report the class test run.

        :param item: pytest item
        :type item: _pytest.nodes.Item
        """
        if item.reports:
            item.ihook.pytest_runtest_logstart(nodeid=item.nodeid, location=item.location)
            for report in item.reports:
                item.ihook.pytest_runtest_logreport(report=report)
            item.ihook.pytest_runtest_logfinish(nodeid=item.nodeid, location=item.location)

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_protocol(self, item, nextitem):
        """
        Run the test protocol.

        :param item: pytest item
        :type item: _pytest.nodes.Item
        :param nextitem: next pytest item
        :type nextitem: _pytest.nodes.Item
        """
        if item.cls is None or self.rerun_max == 0:  # ignore non-class items or plugin disabled
            return False

        if getattr(item, "reports", None) is not None:  # report if called with reports entity should be ignored
            item.reports = None
            return True

        cls = item.getparent(pytest.Class)
        cls_name = cls.name

        if cls_name not in self.rerun_classes:  # ignore if class already passed
            self.rerun_classes.append(cls_name)
        else:
            return False

        siblings = [item]
        items = item.session.items
        index = items.index(item)

        for i in items[index + 1 :]:
            siblings.append(i)
            if item.cls != i.cls:
                break
        if siblings[-1].cls == item.cls:
            siblings.append(None)

        reports = []
        all_passed = False
        rerun_count = 0
        initial_state = self._save_parent_initial_state(cls)
        while not all_passed and rerun_count < self.rerun_max:
            reports.append([])
            all_passed = True
            for i in range(len(siblings) - 1):
                nextitem = siblings[i + 1] if siblings[i + 1] is not None else siblings[0]
                siblings[i].reports = runtestprotocol(siblings[i], nextitem=nextitem, log=False)

                for report in siblings[i].reports:
                    if report.failed and not hasattr(report, "wasxfail") and report.when == "call":
                        if rerun_count < self.rerun_max - 1:
                            report.outcome = "rerun"
                        else:
                            report.outcome = "failed"
                        all_passed = False
                    else:
                        if report.failed and report.when == "setup":
                            print(f"Something really bad happened: {report.longrepr}")
                            return False
                    reports[rerun_count].append(report)
                    if not all_passed:
                        break  # fail fast

                if not all_passed:
                    rerun_count += 1
                    break  # fail fast

            if not all_passed and rerun_count < self.rerun_max:
                # Drop failed fixtures and cache
                self._remove_cached_results_from_failed_fixtures(item)
                item.session._setupstate.stack = {}  # pylint: disable=protected-access
                # Teardown the class and emulate recreation of it
                item.session._setupstate.teardown_exact(None)
                # We can't replace the class because session-scoped fixtures will be lost
                cls, siblings = self._recreate_test_class(cls, siblings, initial_state)
                item.parent = cls  # ensure that we're using updated class
                item.session._setupstate.setup(cls)  # force class setup like "first item"
                print(f"Rerunning {cls_name} - {rerun_count} time(s) after {self.delay} seconds")
                sleep(self.delay)

        item.reports = self._process_reports(reports)
        self._report_run(item)  # report all the runs
        item.session._setupstate.teardown_exact(None)  # force class teardown like "last item"
        return True

    def _save_parent_initial_state(self, parent):
        """
        Save the parent initial state.

        :param item: pytest item
        :type item: _pytest.nodes.Item
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
                attrs[attr_name] = deepcopy(attr_value)
        return attrs

    def _set_parent_initial_state(self, parent, state):
        """
        Set the parent initial state.

        :param item: pytest item
        :type item: _pytest.nodes.Item
        :param state: parent initial state
        :type state: dict
        """
        for attr_name, attr_value in state.items():
            setattr(parent.obj, attr_name, deepcopy(attr_value))
        return parent

    def _recreate_test_class(self, cls: pytest.Class, siblings: list, initial_state: dict) -> tuple:
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

        # TODO: Call class-scoped fixtures

        return cls, siblings

    def _process_reports(self, rerun_reports: list) -> list:
        """
        Process the reports.

        :param rerun_reports: list of rerun reports
        :type rerun_reports: list
        :return: item reports
        :rtype: list
        """
        new_reports = []
        if not self.only_last:
            if len(rerun_reports) > 1:
                for reports in rerun_reports[:-1]:
                    for report in reports:
                        if report.when == "call":
                            report.outcome = "rerun"
                    new_reports += reports
        new_reports += rerun_reports[-1]
        return new_reports

    def _remove_cached_results_from_failed_fixtures(self, item):
        """
        Remove all cached_result attributes from every fixture.

        :param item: pytest item
        :type item: _pytest.nodes.Item
        """
        cached_result = "cached_result"
        fixture_info = getattr(item, "_fixtureinfo", None)
        for fixture_def_str in getattr(fixture_info, "name2fixturedefs", ()):
            fixture_defs = fixture_info.name2fixturedefs[fixture_def_str]
            for fixture_def in fixture_defs:
                if getattr(fixture_def, cached_result, None) is not None:
                    result, _, err = getattr(fixture_def, cached_result)
                    if err:  # Deleting cached results for only failed fixtures
                        setattr(fixture_def, cached_result, None)


def pytest_configure(config):
    """
    Configure the plugin.

    :param config: pytest config
    :type config: _pytest.config.Config
    """
    if config.getoption("--rerun-class-max") > 0:
        rerun_plugin = RerunClassPlugin(config)
        config.pluginmanager.register(rerun_plugin, "rerun_class_plugin")
