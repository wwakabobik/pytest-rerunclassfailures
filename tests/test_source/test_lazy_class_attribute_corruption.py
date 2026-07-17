"""Test that a lazily-created class attribute doesn't leak stale/mutated state across reruns.

Regression test: a class-scope fixture that lazily creates a shared object only if it
doesn't already exist (``if not hasattr(request.cls, "user"): request.cls.user = ...``)
previously left that object attached to the class across reruns, even though the fixture
itself was genuinely re-invoked - because the lazy-creation guard saw the stale attribute
and skipped recreating it, leaking whatever a previous, aborted attempt mutated it to.
"""

import pytest


class LazyUser:  # pylint: disable=too-few-public-methods
    """Simple mutable object standing in for something like a test user/session."""

    def __init__(self, name):
        """Store the given name on a fresh instance."""
        self.name = name


@pytest.fixture(scope="class", autouse=True)
def lazy_user_fixture(request):
    """Class-scope fixture that only creates request.cls.user if it doesn't already exist."""
    if not hasattr(request.cls, "user"):
        request.cls.user = LazyUser(name="fresh")


class TestLazyClassAttributeCorruption:
    """Test class proving the lazily-created attribute is reset, not left stale, on rerun."""

    def test_lazy_attribute_is_fresh(self):
        """Must see a fresh user on every attempt, never one mutated by a prior attempt."""
        assert self.user.name == "fresh"  # type: ignore  # pylint: disable=no-member

    def test_lazy_attribute_mutated_then_forced_failure(self):
        """Mutate the lazily-created attribute, then force a rerun."""
        self.user.name = "mutated-by-previous-attempt"  # type: ignore  # pylint: disable=no-member
        assert False
