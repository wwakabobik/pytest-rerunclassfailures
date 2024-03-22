"""This is a test module class and separate test functions"""


class TestClassWithNeighbours:
    """This is class with neighbours"""

    def test_neighbour_true(self):
        """This class test 1"""
        assert True

    def test_neighbour_false(self):
        """This class test 2"""
        assert False


def test_neighbour_true():
    """This non-class test 1"""
    assert True


def test_neighbour_false():
    """This non-class test 2"""
    assert False
