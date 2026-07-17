"""This test checks that the plugin correctly handles a class attributes and fixtures"""


def test_class_attributes_non_init(run_default_tests):  # pylint: disable=W0613
    """
    This test check test attributes that are not initialized in the class

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_non_init_attributes.py")
    assert return_code == 1
    assert output.count("RERUN") == 3
    assert output.count("PASSED") == 2
    assert " 1 failed, 2 passed, 3 rerun in " in output
    assert "test_non_init_attribute_forced_failure FAILED" in output


def test_class_attributes_function_scope_fixture(run_default_tests):  # pylint: disable=W0613
    """
    This test check attribute are set by the fixture in the function scope

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_function_fixture_attributes.py")
    assert return_code == 1
    assert output.count("RERUN") == 3
    assert output.count("PASSED") == 2
    assert " 1 failed, 2 passed, 3 rerun in " in output
    assert "test_function_scope_fixture_attribute_forced_failure FAILED" in output


def test_class_attributes_ext_function_scope_fixture(run_default_tests):  # pylint: disable=W0613
    """
    This test check attribute are set by the fixture in the function scope (outside of class)

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_ext_function_fixture_attributes.py")
    assert return_code == 1
    assert output.count("RERUN") == 3
    assert output.count("PASSED") == 2
    assert " 1 failed, 2 passed, 3 rerun in " in output
    assert "test_ext_function_scope_fixture_attribute_forced_failure FAILED" in output


def test_class_attributes_class_scope_fixture(run_default_tests):  # pylint: disable=W0613
    """
    This test check attribute are set by the fixture in the class scope

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_class_fixture_attributes.py")
    assert return_code == 1
    assert output.count("RERUN") == 3
    assert output.count("PASSED") == 2
    assert " 1 failed, 2 passed, 3 rerun in " in output
    assert "test_class_scope_fixture_attribute_forced_failure FAILED" in output


def test_class_attributes_list_handling(run_default_tests):  # pylint: disable=W0613
    """
    This test check that list type attributes are handled correctly

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_list_attributes.py")
    assert return_code == 1
    assert output.count("RERUN") == 3
    assert output.count("PASSED") == 2
    assert " 1 failed, 2 passed, 3 rerun in " in output
    assert "test_list_type_attribute_forced_failure FAILED" in output


def test_class_attributes_dict_handling(run_default_tests):  # pylint: disable=W0613
    """
    This test check that dict type attributes are handled correctly

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_dict_attributes.py")
    assert return_code == 1
    assert output.count("RERUN") == 3
    assert output.count("PASSED") == 2
    assert " 1 failed, 2 passed, 3 rerun in " in output
    assert "test_dict_type_attribute_forced_failure FAILED" in output


def test_class_attributes_function_params(run_default_tests):  # pylint: disable=W0613
    """
    This test check function parameters are handled correctly

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_function_attributes.py")
    assert return_code == 1
    assert output.count("RERUN") == 3
    assert output.count("PASSED") == 2
    assert " 1 failed, 2 passed, 3 rerun in " in output
    assert "test_function_params_attribute_forced_failure FAILED" in output


def test_class_attributes_function_fixtures(run_default_tests):  # pylint: disable=W0613
    """
    This test proves that a class attribute set as a side effect of a function-scope
    fixture whose return value is consumed as a test parameter is reset correctly across
    reruns - including the per-item bound instance (Function._instance/_obj), which
    pytest otherwise memoizes on the same Item object this plugin reruns

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_function_attributes_as_fixtures.py")
    assert return_code == 1
    assert output.count("RERUN") == 3
    assert output.count("PASSED") == 2
    assert " 1 failed, 2 passed, 3 rerun in " in output
    assert "test_function_fixtures_attribute_forced_failure FAILED" in output


def test_class_attributes_class_scope_fixture_teardown(run_default_tests):  # pylint: disable=W0613
    """
    This test proves the class-scope fixture's real finalizer (yield teardown) is
    genuinely re-invoked between reruns, not just that request.cls attributes are reset.

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_class_fixture_teardown_side_effects.py")
    assert return_code == 0
    assert output.count("RERUN") == 2
    assert " 2 passed, 2 rerun in " in output


def test_class_attributes_class_scope_fixture_dependency_chain(run_default_tests):  # pylint: disable=W0613
    """
    This test proves that a chain of dependent class-scope fixtures (one requesting
    another) is torn down in the correct order between reruns, via pytest's own
    finalizer chain rather than any manual per-fixture bookkeeping.

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_class_fixture_dependency_chain.py")
    assert return_code == 0
    assert output.count("RERUN") == 2
    assert " 2 passed, 2 rerun in " in output


def test_class_attributes_lazy_attribute_not_corrupted(run_default_tests):  # pylint: disable=W0613
    """
    Regression test: a lazily-created class attribute (created by a fixture only if it
    doesn't already exist) must be removed between reruns, not left mutated from a
    previous, aborted attempt.

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_lazy_class_attribute_corruption.py")
    assert return_code == 1
    assert output.count("RERUN") == 2
    assert "test_lazy_attribute_is_fresh PASSED" in output
    assert " 1 failed, 1 passed, 2 rerun in " in output


def test_class_attributes_unpickable(run_default_tests):  # pylint: disable=W0613
    """
    This test check that unpickleable attributes are handled correctly

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_unpickleable_attributes.py")
    assert return_code == 1
    assert output.count("RERUN") == 3
    assert output.count("PASSED") == 2
    assert " 1 failed, 2 passed, 3 rerun in " in output
    assert "test_unpickleable_attributes_initial PASSED [ 33%]" in output
    assert "test_unpickleable_attributes_changed PASSED [ 66%]" in output
    assert "test_unpickleable_attributes_fail FAILED [100%]" in output
