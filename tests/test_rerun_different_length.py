"""This test checks that plugin correctly handles tests that fail on the second run and pass on the first run"""


def test_rerun_consistency_lesser(run_tests_with_plugin):  # pylint: disable=W0613
    """
    This test checks that the plugin handles different rerun lengths correctly (flacky test).
    This test checks case when first run is longer than the second run.

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    args = ["--rerun-class-max=1"]
    error_code, output = run_tests_with_plugin("tests/test_source/test_failed_on_second_run.py", args)
    expected_terminal_outcome = """=================================== FAILURES ===================================
______________________ TestFailedOnSecondRun.test_flacky _______________________
tests/test_source/test_failed_on_second_run.py:20: in test_flacky
    assert False
E   assert False
==================================== RERUNS ====================================
RERUN tests/test_source/test_failed_on_second_run.py::TestFailedOnSecondRun::test_always_pass
RERUN tests/test_source/test_failed_on_second_run.py::TestFailedOnSecondRun::test_flacky
RERUN tests/test_source/test_failed_on_second_run.py::TestFailedOnSecondRun::test_always_fail
tests/test_source/test_failed_on_second_run.py:24: in test_always_fail
    assert False
E   assert False"""
    assert error_code == 1
    assert output.count("RERUN") == 7
    assert output.count("PASSED") == 1
    assert output.count("FAILED") == 2
    assert output.count("test_always_fail RERUN") == 1
    assert output.count("test_flacky RERUN") == 1
    assert output.count("test_flacky FAILED") == 1
    assert " 1 failed, 1 passed, 3 rerun " in output
    assert expected_terminal_outcome in output


def test_rerun_consistency_bigger(run_tests_with_plugin):  # pylint: disable=W0613
    """
    This test checks that the plugin handles different rerun lengths correctly (flacky test).
    This test checks case when first run is shorter than the second run.

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    args = ["--rerun-class-max=1"]
    error_code, output = run_tests_with_plugin("tests/test_source/test_failed_on_first_run.py", args)
    expected_terminal_outcome = """=================================== FAILURES ===================================
_______________________ TestFailedOnFirstRun.test_flacky _______________________
tests/test_source/test_failed_on_first_run.py:20: in test_flacky
    assert False
E   assert False
==================================== RERUNS ====================================
RERUN tests/test_source/test_failed_on_first_run.py::TestFailedOnFirstRun::test_always_pass
RERUN tests/test_source/test_failed_on_first_run.py::TestFailedOnFirstRun::test_flacky
tests/test_source/test_failed_on_first_run.py:20: in test_flacky
    assert False
E   assert False"""
    print(output)
    assert error_code == 1
    assert output.count("RERUN") == 5
    assert output.count("PASSED") == 1
    assert output.count("FAILED") == 2
    assert output.count("test_always_fail SKIPPED") == 1
    assert output.count("test_flacky RERUN") == 1
    assert output.count("test_flacky FAILED") == 1
    assert " 1 failed, 1 passed, 1 skipped, 2 rerun " in output
    assert expected_terminal_outcome in output
