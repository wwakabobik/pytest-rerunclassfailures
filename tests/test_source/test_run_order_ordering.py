"""This module contains class with non-default order of tests (ordering plugin)"""

import pytest


class TestRunOrdering:
    """This class contains tests with non-default order of tests"""

    def test_run_order_1(self):
        """This test always passes"""
        assert True

    @pytest.mark.run(order=2)
    def test_run_order_2(self):
        """This test always passes"""
        assert True

    def test_run_order_3(self):
        """This test always fails"""
        assert False

    @pytest.mark.run(order=1)
    def test_run_order_4(self):
        """This test always passes"""
        assert True
