"""Test class with function (fixtures) attributes"""

from random import choice

import pytest

random_attribute_value = choice((42, "abc", None))


@pytest.fixture(scope="function")
def function_fixture(request):
    """Fixture to set function attribute"""
    request.cls.attribute = "initial"
    return "initial"


@pytest.fixture(scope="function")
def function_fixture_secondary(request):
    """Fixture to set function attribute"""
    request.cls.attribute = "secondary"
    return "secondary"


class TestFunctionFixturesAttributes:
    """Test class with function params attributes"""

    def test_function_fixtures_attribute_initial(self, function_fixture):  # pylint: disable=W0621
        """Test function fixture attribute at the beginning of the class"""
        assert self.attribute == "initial"
        assert function_fixture == "initial"

    def test_function_fixtures_attribute_recheck(self, function_fixture_secondary):  # pylint: disable=W0621
        """Test function fixture attribute after changing attribute value"""
        assert self.attribute == "secondary"  # type: ignore  # pylint: disable=E0203
        assert function_fixture_secondary == "secondary"
        self.attribute = random_attribute_value  # type: ignore  # pylint: disable=attribute-defined-outside-init
        # attribute is changed, but fixture is not
        assert self.attribute == random_attribute_value
        assert function_fixture_secondary == "secondary"

    def test_function_fixtures_attribute_forced_failure(self):
        """Test function fixture attribute to be forced failure"""
        assert False
