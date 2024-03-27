"""This module contains class with different test statuses"""

import pytest


class TestDifferentStatuses:
    """Test class with different statuses"""

    def test_pass(self):
        """This test always passes"""
        assert True

    @pytest.mark.xfail
    def test_xpass(self):
        """This test always xpasses"""
        assert True

    @pytest.mark.xfail
    def test_xfail(self):
        """This test always xfails"""
        assert False

    def test_skip(self):
        """This test always skips"""
        pytest.skip("Skip this test")

    def test_fail(self):
        """This test always fails"""
        assert False

    def test_not_reachable_pass(self):
        """This test is not reachable"""
        assert True

    @pytest.mark.xfail
    def test_not_reachable_xpass(self):
        """This test is not reachable"""
        assert False

    @pytest.mark.xfail
    def test_not_reachable_xfail(self):
        """This test is not reachable"""
        assert True

    def test_not_reachable_skip(self):
        """This test is not reachable"""
        pytest.skip("Skip this test")

    def test_not_reachable_fail(self):
        """This test is not reachable"""
        assert False
