"""This module contains class with failing tests at call stage"""


class TestFailInCall:  # pylint: disable=too-few-public-methods
    """This test checks that the plugin correctly handles failure at call stage"""

    def test_call_fail(self):
        """This test should fail at call stage"""
        assert False, "Call error"
