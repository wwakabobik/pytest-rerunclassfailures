"""This class has exactly the same name as other"""


class TestSameClass:
    """This class has exactly the same name as other"""

    def test_same_class_differs_true(self):
        """This test always passes"""
        assert True

    def test_same_class_differs_false(self):
        """This test always fails"""
        assert False
