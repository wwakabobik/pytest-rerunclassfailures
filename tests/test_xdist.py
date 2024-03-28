"""This test checks that the plugin correctly work with xdist plugin"""


def test_xdist_disabled(run_default_tests):  # pylint: disable=W0613
    """
    This test checks that the plugin correctly work with xdist plugin disabled

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_basic.py", "-n=0 --dist=loadscope")
    assert return_code == 1
    assert output.count("RERUN") == 2
    assert output.count("PASSED") == 1
    assert " 1 failed, 1 passed, 1 skipped, 2 rerun " in output
    assert "[gw" not in output


def test_xdist_one_node(run_default_tests):  # pylint: disable=W0613
    """
    This test checks that the plugin correctly work with xdist plugin with one node

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_basic.py", "-n=1 --dist=loadscope")
    assert return_code == 1
    assert output.count("RERUN") == 2
    assert output.count("PASSED") == 1
    assert " 1 failed, 1 passed, 1 skipped, 2 rerun " in output
    assert output.count("[gw0] ") == 6


def test_xdist_two_nodes_one_class(run_default_tests):  # pylint: disable=W0613
    """
    This test checks that the plugin correctly work with xdist plugin with one node

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_basic.py", "-n=2 --dist=loadscope")
    assert return_code == 1
    assert output.count("RERUN") == 2
    assert output.count("PASSED") == 1
    assert " 1 failed, 1 passed, 1 skipped, 2 rerun in " in output
    assert output.count("[gw0] ") == 6
    assert output.count("[gw1] ") == 0


def test_xdist_two_nodes_two_classes(run_default_tests):  # pylint: disable=W0613
    """
    This test checks that the plugin correctly work with xdist plugin with one node

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests(
        "tests/test_source/test_several_classes_in_module.py", "-n=2 --dist=loadscope"
    )
    assert return_code == 1
    assert output.count("] RERUN") == 4
    assert output.count("] PASSED") == 2
    assert output.count("] FAILED") == 2
    assert " 2 failed, 2 passed, 4 rerun in " in output
    assert output.count("[gw0] ") == 5
    assert output.count("[gw1] ") == 5


def test_xdist_loadscope_not_used(run_default_tests):  # pylint: disable=W0613
    """
    This test checks that the plugin correctly work with xdist plugin even if loadscope is not used

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_several_classes_in_module.py", "-n=4")
    assert return_code == 1
    assert "[gw2]" in output
    assert "[gw3]" in output
    assert output.count("] RERUN") == 4  # count of rerun tests remains the same, but they are distributed between nodes


def test_xdist_ordering_methods(run_default_tests):  # pylint: disable=W0613
    """
    This test checks that the plugin correctly work with ordered tests and xdist plugin

    :param run_default_tests: fixture to run pytest with the plugin and default arguments
    :type run_default_tests: function
    """
    return_code, output = run_default_tests("tests/test_source/test_run_order_both.py", "-n=2 --dist=loadscope")
    assert return_code == 1
    assert output.count("] RERUN ") == 8
    assert " 2 failed, 6 passed, 8 rerun " in output
