"""This test checks that the plugin correctly handles any states of tests"""


def test_different_statuses(run_default_tests):  # pylint: disable=W0613
    """
    This test check different outcomes of tests

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """

    return_code, output = run_default_tests("tests/test_source/test_different_statuses.py")
    assert return_code == 1
    assert output.count("tests/test_source/test_different_statuses.py::TestDifferentStatuses::test_pass") == 2
    assert output.count("tests/test_source/test_different_statuses.py::TestDifferentStatuses::test_xpass") == 2
    assert output.count("tests/test_source/test_different_statuses.py::TestDifferentStatuses::test_xfail") == 3
    assert output.count("tests/test_source/test_different_statuses.py::TestDifferentStatuses::test_skip") == 2
    assert output.count("tests/test_source/test_different_statuses.py::TestDifferentStatuses::test_fail") == 3
    assert output.count("tests/test_source/test_different_statuses.py::test_not_reachable_pass") == 0
    assert output.count("tests/test_source/test_different_statuses.py::test_not_reachable_xpass") == 0
    assert output.count("tests/test_source/test_different_statuses.py::test_not_reachable_xfail") == 0
    assert output.count("tests/test_source/test_different_statuses.py::test_not_reachable_skip") == 0
    assert output.count("tests/test_source/test_different_statuses.py::test_not_reachable_fail") == 0
    assert " 1 failed, 1 passed, 6 skipped, 1 xfailed, 1 xpassed, 5 rerun in " in output
    assert "FAILED [ 50%]" in output
    assert output.count("RERUN") == 5


def test_statuses_fail_fast(run_default_tests):  # pylint: disable=W0613
    """
    This test checks that rest of the test in test class after failure are not run

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_different_statuses.py")
    assert return_code == 1
    assert output.count("tests/test_source/test_different_statuses.py::TestDifferentStatuses::test_not_reachable_") == 5
    assert output.count("Skipping test due to class execution was aborted during rerun") == 5
    assert "test_not_reachable_pass SKIPPED [ 60%]" in output
    assert "test_not_reachable_xpass SKIPPED [ 70%]" in output
    assert "test_not_reachable_xfail SKIPPED [ 80%]" in output
    assert "test_not_reachable_skip SKIPPED [ 90%]" in output
    assert "test_not_reachable_fail SKIPPED [100%]" in output
