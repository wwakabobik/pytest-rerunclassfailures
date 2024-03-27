"""This module contains class with non-default order of tests both plugins"""

import pytest


class TestRunOrder:
    """This class contains tests with non-default order of tests"""

    def test_run_order_1(self):
        """This test always passes"""
        assert True

    @pytest.mark.order(2)
    def test_run_order_2(self):
        """This test always passes"""
        assert True

    def test_run_order_3(self):
        """This test always fails"""
        assert False

    @pytest.mark.order(1)
    def test_run_order_4(self):
        """This test always passes"""
        assert True
