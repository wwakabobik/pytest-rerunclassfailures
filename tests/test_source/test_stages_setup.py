"""This module contains class problems with setup stage"""

import pytest


class TestFailInSetup:
    """This test checks that the plugin correctly handles failure at any stage of the test"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup method that always fails"""
        assert False, "Setup error"

    def test_never_run_after_setup(self):
        """This test should never run after setup failure"""
        assert True
