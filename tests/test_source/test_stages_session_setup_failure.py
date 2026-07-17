"""
A session-scope fixture that always fails during setup.

Regression test: see test_stages_module_setup_failure.py for the full rationale -
session-scope fixtures must never be silently retried between class reruns.
"""

import pytest


@pytest.fixture(scope="session", autouse=True)
def session_setup():
    """Session-scope fixture that always fails during setup."""
    assert False, "Session setup error"  # pylint: disable=broad-exception-raised


class TestFailInSessionSetup:  # pylint: disable=too-few-public-methods
    """Check that a failing session-scope fixture never crashes the plugin."""

    def test_after_session_setup(self):
        """Test should never run, the session fixture always fails."""
        assert True
