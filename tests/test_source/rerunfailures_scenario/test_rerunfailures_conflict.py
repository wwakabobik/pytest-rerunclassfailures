"""Test class used to prove the pytest-rerunfailures conflict detection fires/is bypassed."""


class TestRerunfailuresConflict:  # pylint: disable=too-few-public-methods

    """A trivial passing test class; the interesting behavior is in conftest.py + the CLI flag."""  # fmt: skip

    def test_placeholder(self):
        """Never actually reached when the conflict is correctly detected and raised."""
        assert True
