"""This class has exactly the same name as other within module"""


class TestSameModuleClass:
    """This class has exactly the same name as other"""

    def test_same_class_true(self):
        """This test always passes"""
        assert True

    def test_same_class_false(self):
        """This test always fails"""
        assert False


class TestSameModuleClass:  # type: ignore  # pylint: disable=function-redefined
    """This class has exactly the same name as other"""

    def test_same_class_true(self):
        """This test always passes"""
        assert True

    def test_same_class_false(self):
        """This test always fails"""
        assert False
