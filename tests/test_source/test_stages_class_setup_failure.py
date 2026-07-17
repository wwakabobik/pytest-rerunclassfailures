"""A class-scope fixture that fails on its first setup attempt only."""

import pytest

attempts: list = []


class TestFailInClassSetup:

    """Check that a class-scope fixture failing during setup is genuinely retried."""  # fmt: skip

    @pytest.fixture(scope="class", autouse=True)
    def class_setup(self, request):  # pylint: disable=unused-argument
        """Class-scope fixture that fails on the first attempt, then succeeds."""
        attempts.append("setup")
        if len(attempts) == 1:
            assert False, "Class setup error"  # pylint: disable=broad-exception-raised

    def test_after_class_setup(self):
        """Test should eventually pass once the class-scope fixture succeeds."""
        assert True
