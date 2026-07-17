"""Test class-scope fixture whose yield-based finalizer has real side effects"""

import pytest

teardown_calls: list = []


@pytest.fixture(scope="class", autouse=True)
def class_fixture_with_teardown(request):
    """Class-scope fixture that records when its real teardown code actually runs"""
    request.cls.setup_count = len(teardown_calls) + 1
    yield
    teardown_calls.append("torn_down")


@pytest.mark.usefixtures("class_fixture_with_teardown")
class TestClassScopeFixtureTeardown:
    """Test class proving the class-scope fixture is genuinely re-invoked on rerun"""

    def test_class_fixture_teardown_initial(self):
        """Setup count must match how many times the fixture has actually (re)run"""
        assert self.setup_count == len(teardown_calls) + 1  # type: ignore

    def test_class_fixture_teardown_forced_failure(self):
        """Fails until the fixture's real finalizer has run at least once between reruns"""
        assert len(teardown_calls) >= 1
