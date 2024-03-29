"""This test checks that the plugin correctly handles failure at any stage of the test"""


def test_failure_stages_setup(run_default_tests):  # pylint: disable=W0613
    """
    This test check test attributes that are not initialized in the class

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_stages_setup.py")
    assert return_code == 1
    assert output.count("RERUN ") == 1
    assert output.count("ERROR ") == 3
    assert " 1 error, 1 rerun in " in output
    assert "= ERRORS =" in output


def test_failure_stages_call(run_default_tests):  # pylint: disable=W0613
    """
    This test check test attributes that are not initialized in the class

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_stages_call.py")
    assert return_code == 1
    assert output.count("RERUN ") == 1
    assert output.count("FAILED ") == 2
    assert " 1 failed, 1 rerun in " in output


def test_failure_stages_teardown_function(run_default_tests):  # pylint: disable=W0613
    """
    This test check test attributes that are not initialized in the class

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_stages_teardown_func.py")
    assert return_code == 1
    assert output.count("PASSED ") == 1
    assert output.count("SKIPPED ") == 2
    assert output.count("ERROR ") == 3
    assert output.count("RERUN ") == 1
    assert " 1 passed, 1 skipped, 1 error, 1 rerun in " in output
    assert "= ERRORS =" in output
    assert 'assert False, "Teardown error"' in output


def test_failure_stages_teardown_class_fails(run_default_tests):  # pylint: disable=W0613
    """
    This test check test attributes that are not initialized in the class

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_stages_teardown_class.py")
    assert return_code == 1
    assert output.count("PASSED ") == 1
    assert output.count("RERUN ") == 2
    assert output.count("ERROR ") == 0
    assert output.count("FAILED ") == 2
    assert " 1 failed, 1 passed, 2 rerun in " in output
    assert "Exception during teardown: AssertionError: Class teardown error" in output


def test_failure_stages_teardown_class_without_aborting(run_default_tests):  # pylint: disable=W0613
    """
    This test check test attributes that are not initialized in the class

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_stages_teardown_class_pure.py")
    assert return_code == 0
    assert output.count("PASSED ") == 1
    assert output.count("RERUN ") == 0
    assert output.count("ERROR ") == 0
    assert output.count("FAILED ") == 0
    assert " 1 passed in " in output
    assert "Exception during teardown: AssertionError: Class teardown error" in output
