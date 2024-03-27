"""This module contains several test classes"""


class TestSeveralModuleClass:
    """This class some unique name"""

    def test_several_class_true(self):
        """This test always passes"""
        assert True

    def test_several_class_false(self):
        """This test always fails"""
        assert False


class TestSeveralOtherModuleClass:
    """This class in same module as any other"""

    def test_several_class_true(self):
        """This test always passes"""
        assert True

    def test_several_class_false(self):
        """This test always fails"""
        assert False
