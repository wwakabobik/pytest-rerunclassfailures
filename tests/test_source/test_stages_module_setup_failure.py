"""A module-scope fixture that always fails during setup.

Regression test: previously, `_remove_cached_results_from_failed_fixtures` cleared
`cached_result` for ANY failed fixture regardless of scope, which (a) violated the
module/session scope contract by silently retrying a fixture meant to run once per
module, and (b) left `FixtureDef._finalizers` non-empty, causing a crash
(`assert not self._finalizers`) the next time the class was rerun.
"""

import pytest

attempts: list = []


@pytest.fixture(scope="module", autouse=True)
def module_setup(request):  # pylint: disable=unused-argument
    """Module-scope fixture that always fails during setup."""
    attempts.append("setup")
    assert False, "Module setup error"  # pylint: disable=broad-exception-raised


class TestFailInModuleSetup:  # pylint: disable=too-few-public-methods
    """Check that a failing module-scope fixture never crashes the plugin."""

    def test_after_module_setup(self):
        """Test should never run, the module fixture always fails."""
        assert True
