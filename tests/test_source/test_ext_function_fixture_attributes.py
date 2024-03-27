"""Test class with external function scope fixture attributes"""

from random import choice

import pytest

random_attribute_value = choice((42, "abc", None))


@pytest.fixture(autouse=True, scope="function")
def external_fixture(request):
    """Fixture to set class attribute (function-scope, outside of the class)"""
    request.cls.attribute = "initial"  # pylint: disable=attribute-defined-outside-init


class TestWithExtFunctionScopeFixtureAttributes:
    """Test class with attributes set by function-scope fixtures"""

    def test_ext_function_fixture_attribute_initial(self):
        """Test function scope fixture attribute at the beginning of the class"""
        assert self.attribute == "initial"

    def test_ext_function_scope_fixture_attribute_recheck(self):
        """Test function scope fixture attribute after changing attribute value"""
        self.attribute = random_attribute_value  # type: ignore  # pylint: disable=attribute-defined-outside-init
        assert self.attribute == random_attribute_value

    def test_ext_function_scope_fixture_attribute_forced_failure(self):
        """Test function scope fixture attribute to be forced failure"""
        assert False
