"""This class contains tests that always fail on the first run and pass on the second run"""

global_state = False  # pylint: disable=invalid-name


class TestFailedOnFirstRun:
    """This class fails on the first run and passes on the second run"""

    def test_always_pass(self):
        """This test always passes"""
        assert True

    def test_flacky(self):
        """This test fails on the second run and passes on the first run"""
        global global_state  # pylint: disable=global-statement
        if global_state:
            global_state = False
            assert True
        else:
            assert False

    def test_always_fail(self):
        """This test always fails"""
        assert False
