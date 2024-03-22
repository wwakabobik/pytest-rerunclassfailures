"""This class has exactly the same test name as other"""


class TestSameTestInClass:  # pylint: disable=too-few-public-methods
    """This class has exactly the same name as other"""

    def test_same_test(self):
        """This test always passes"""
        assert True

    def test_same_test(self):  # type: ignore  # pylint: disable=function-redefined
        """This test always fails"""
        assert False
