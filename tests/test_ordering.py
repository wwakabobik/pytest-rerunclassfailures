"""This test checks that the plugin correctly work with ordered tests"""


def test_ordering_non_default_ordering(run_default_tests):  # pylint: disable=W0613
    """
    This test checks that the plugin correctly work with ordered tests

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_run_order_ordering.py")
    assert return_code == 1
    assert output.count("tests/test_source/test_run_order_ordering.py::TestRunOrdering::test_run_order_1") == 2
    assert output.count("tests/test_source/test_run_order_ordering.py::TestRunOrdering::test_run_order_2") == 2
    assert output.count("tests/test_source/test_run_order_ordering.py::TestRunOrdering::test_run_order_3") == 3
    assert output.count("tests/test_source/test_run_order_ordering.py::TestRunOrdering::test_run_order_4") == 2
    assert output.count("RERUN [") == 4
    assert output.count("PASSED [") == 3
    assert output.count("FAILED [") == 1
    assert "test_run_order_4 RERUN [ 25%]" in output
    assert "test_run_order_2 RERUN [ 50%]" in output
    assert "test_run_order_1 RERUN [ 75%]" in output
    assert "test_run_order_3 FAILED [100%]" in output
    assert "test_run_order_4 PASSED [ 25%]" in output
    assert "test_run_order_2 PASSED [ 50%]" in output
    assert "test_run_order_1 PASSED [ 75%]" in output
    assert "test_run_order_3 FAILED [100%]" in output
    assert " 1 failed, 3 passed, 4 rerun " in output


def test_ordering_non_default_order(run_default_tests):  # pylint: disable=W0613
    """
    This test checks that the plugin correctly work with ordered tests

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_run_order_order.py")
    assert return_code == 1
    assert output.count("tests/test_source/test_run_order_order.py::TestRunOrder::test_run_order_1") == 2
    assert output.count("tests/test_source/test_run_order_order.py::TestRunOrder::test_run_order_2") == 2
    assert output.count("tests/test_source/test_run_order_order.py::TestRunOrder::test_run_order_3") == 3
    assert output.count("tests/test_source/test_run_order_order.py::TestRunOrder::test_run_order_4") == 2
    assert output.count("RERUN [") == 4
    assert output.count("PASSED [") == 3
    assert output.count("FAILED [") == 1
    assert "test_run_order_4 RERUN [ 25%]" in output
    assert "test_run_order_2 RERUN [ 50%]" in output
    assert "test_run_order_1 RERUN [ 75%]" in output
    assert "test_run_order_3 FAILED [100%]" in output
    assert "test_run_order_4 PASSED [ 25%]" in output
    assert "test_run_order_2 PASSED [ 50%]" in output
    assert "test_run_order_1 PASSED [ 75%]" in output
    assert "test_run_order_3 FAILED [100%]" in output
    assert " 1 failed, 3 passed, 4 rerun " in output


def test_ordering_both_methods(run_default_tests):  # pylint: disable=W0613
    """
    This test checks that the plugin correctly work with ordered tests

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_run_order_both.py")
    assert return_code == 1
    assert output.count("RERUN [") == 8
    assert " 2 failed, 6 passed, 8 rerun " in output
