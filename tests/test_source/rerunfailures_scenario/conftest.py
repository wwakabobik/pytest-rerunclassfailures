"""Registers a minimal stand-in plugin under the name pytest-rerunfailures uses, so the
conflict-detection tests below don't need the real pytest-rerunfailures as a dependency."""


class _FakeRerunfailuresPlugin:  # pylint: disable=too-few-public-methods
    """Placeholder standing in for the real pytest-rerunfailures plugin object"""


def pytest_configure(config):
    """Register the fake plugin under the same name pytest-rerunfailures registers as"""
    config.pluginmanager.register(_FakeRerunfailuresPlugin(), "rerunfailures")
