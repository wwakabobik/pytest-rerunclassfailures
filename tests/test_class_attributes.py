"""This test checks that the plugin correctly handles a class attributes and fixtures"""

import pytest


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


@pytest.mark.xfail(reason="This test is expected to fail due to fixtures not reinitialized")
def test_class_attributes_function_fixtures(run_default_tests):  # pylint: disable=W0613
    """
    This test check params obtained or set by fixtures are handled correctly

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_function_attributes_as_fixtures.py")
    assert return_code == 1
    assert output.count("RERUN") == 3
    assert output.count("PASSED") == 2
    assert " 1 failed, 2 passed, 3 rerun in " in output
    assert "test_function_fixtures_attribute_forced_failure FAILED" in output


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
