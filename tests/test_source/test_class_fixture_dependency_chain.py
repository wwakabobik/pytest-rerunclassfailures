"""Test class-scope fixtures with a dependency chain (one depends on another)."""

import pytest

teardown_order: list = []


@pytest.fixture(scope="class")
def base_fixture():
    """Base class-scope fixture with its own teardown side effect."""
    yield "base"
    teardown_order.append("base")


@pytest.fixture(scope="class")
def dependent_fixture(base_fixture):  # pylint: disable=redefined-outer-name
    """Class-scope fixture that depends on base_fixture."""
    yield f"{base_fixture}-dependent"
    teardown_order.append("dependent")


@pytest.mark.usefixtures("dependent_fixture")
class TestClassFixtureDependencyChain:
    """Test class using a chain of dependent class-scope fixtures."""

    def test_dependency_chain_initial(self, dependent_fixture):  # pylint: disable=redefined-outer-name
        """Test that the dependent fixture resolves the chain correctly."""
        assert dependent_fixture == "base-dependent"

    def test_dependency_chain_forced_failure(self):
        """Force exactly one rerun, then require proof both fixtures tore down in order."""
        if len(teardown_order) < 2:
            assert False, f"forcing rerun (teardown_order={teardown_order!r})"  # pylint: disable=broad-exception-raised
        assert teardown_order == ["dependent", "base"]
