"""Test class with function scope fixture attributes"""

from random import choice

import pytest

random_attribute_value = choice((42, "abc", None))


class TestWithFunctionScopeFixtureAttributes:
    """Test class with attributes set by function-scope fixtures"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Fixture to set class attribute (function-scope, inside of the class)"""
        self.attribute = "initial"  # pylint: disable=attribute-defined-outside-init

    def test_function_fixture_attribute_initial(self):
        """Test function scope fixture attribute at the beginning of the class"""
        assert self.attribute == "initial"

    def test_function_scope_fixture_attribute_recheck(self):
        """Test function scope fixture attribute after changing attribute value"""
        self.attribute = random_attribute_value  # type: ignore  # pylint: disable=attribute-defined-outside-init
        assert self.attribute == random_attribute_value

    def test_function_scope_fixture_attribute_forced_failure(self):
        """Test function scope fixture attribute to be forced failure"""
        assert False
