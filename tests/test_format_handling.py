"""This test check that different type of tests are handled correctly (module, class, test)"""


def test_format_handling_no_class(run_default_tests):  # pylint: disable=W0613
    """
    This test check test with no class in the module will be ignored

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_no_class.py")
    assert return_code == 1
    assert output.count("tests/test_source/test_no_class.py::test_no_class_") == 4
    assert "RERUN" not in output
    assert " 1 failed, 2 passed in " in output


def test_format_handling_same_class(run_default_tests):  # pylint: disable=W0613
    """
    This test check test with the same class name in the module will be rerun correctly

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests(
        ["tests/test_source/test_same_class_1.py", "tests/test_source/test_same_class_2.py"]
    )
    assert return_code == 1
    assert output.count("tests/test_source/test_same_class_1.py::TestSameClass::test_same_class_") == 5
    assert output.count("tests/test_source/test_same_class_2.py::TestSameClass::test_same_class_differs_") == 5
    assert output.count("RERUN") == 4
    assert " 2 failed, 2 passed, 4 rerun in " in output


def test_format_handling_same_class_in_module(run_default_tests):  # pylint: disable=W0613
    """
    This test check test with the same class name in the module will be rerun correctly

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_same_class_in_module.py")
    assert return_code == 1
    assert output.count("tests/test_source/test_same_class_in_module.py::TestSameModuleClass::test_same_class_") == 5
    assert output.count("RERUN") == 2
    assert " 1 failed, 1 passed, 2 rerun in " in output


def test_format_handling_class_with_no_class(run_default_tests):  # pylint: disable=W0613
    """
    This test check test with the same class name in the module will be rerun correctly

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_class_with_no_class.py")
    assert return_code == 1
    assert output.count("tests/test_source/test_class_with_no_class.py::TestClassWithNeighbours::test_neighbour_") == 5
    assert output.count("tests/test_source/test_class_with_no_class.py::test_neighbour_") == 3
    assert output.count("RERUN") == 2
    assert " 2 failed, 2 passed, 2 rerun in " in output


def test_format_handling_same_test_in_class(run_default_tests):  # pylint: disable=W0613
    """
    This test check test with the same test name in the class will be rerun correctly

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_same_test_in_class.py")
    assert return_code == 1
    assert output.count("tests/test_source/test_same_test_in_class.py::TestSameTestInClass::test_same_test") == 3
    assert output.count("RERUN") == 1
    assert " 1 failed, 1 rerun in " in output


def test_format_handling_several_classes_in_module(run_default_tests):  # pylint: disable=W0613
    """
    This test check test with the same test name in the class will be rerun correctly

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_several_classes_in_module.py")
    assert return_code == 1
    assert output.count("tests/test_source/test_several_classes_in_module.py::TestSeveralModuleClass") == 5
    assert output.count("tests/test_source/test_several_classes_in_module.py::TestSeveralOtherModuleClass") == 5
    assert output.count("TestSeveralModuleClass::test_several_class_true RERUN") == 1
    assert output.count("TestSeveralModuleClass::test_several_class_false RERUN") == 1
    assert output.count("TestSeveralOtherModuleClass::test_several_class_true RERUN") == 1
    assert output.count("TestSeveralOtherModuleClass::test_several_class_false RERUN") == 1
    assert output.count("TestSeveralModuleClass::test_several_class_true PASSED") == 1
    assert output.count("TestSeveralOtherModuleClass::test_several_class_true PASSED") == 1
    assert output.count("TestSeveralModuleClass::test_several_class_false FAILED") == 1
    assert output.count("TestSeveralOtherModuleClass::test_several_class_false FAILED") == 1
    assert output.count("RERUN") == 4
    assert " 2 failed, 2 passed, 4 rerun in " in output
