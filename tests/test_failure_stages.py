"""This test checks that the plugin correctly handles failure at any stage of the test."""


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


def test_failure_stages_class_setup_retries(run_default_tests):  # pylint: disable=W0613
    """
    Prove a class-scope fixture that fails during setup is genuinely retried.

    Its real FixtureDef state is reset, not just cached-and-crashing, on the next rerun,
    rather than permanently erroring or crashing the plugin.

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_stages_class_setup_failure.py")
    assert return_code == 0
    assert output.count("RERUN") == 1
    assert " 1 passed, 1 rerun in " in output


def test_failure_stages_module_setup_never_retried(run_default_tests):  # pylint: disable=W0613
    """
    Regression test: a module-scope fixture that fails during setup must consistently error on every rerun.

    Its scope contract forbids retrying it, and it must never crash the plugin itself (see
    test_failure_stages_class_setup_retries for the class-scope counterpart, where retrying IS correct).

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_stages_module_setup_failure.py")
    assert return_code == 1
    assert output.count("RERUN") == 1
    assert " 1 error, 1 rerun in " in output
    assert "assert not self._finalizers" not in output


def test_failure_stages_session_setup_never_retried(run_default_tests):  # pylint: disable=W0613
    """
    Regression test: a session-scope fixture that fails during setup must consistently error on every rerun.

    It must never crash the plugin itself.

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_stages_session_setup_failure.py")
    assert return_code == 1
    assert output.count("RERUN") == 1
    assert " 1 error, 1 rerun in " in output
    assert "assert not self._finalizers" not in output


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
    print(output)
    # The class-scope fixture is now genuinely torn down and re-set-up between the two
    # attempts (see _teardown_class_and_below), so its always-failing teardown legitimately
    # fires once per attempt (initial run + 1 rerun), independent of the installed pytest version.
    assert output.count("Exception during teardown: AssertionError: Class teardown error") == 2


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
