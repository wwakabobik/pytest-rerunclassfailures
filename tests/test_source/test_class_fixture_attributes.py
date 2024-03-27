"""Test class with class scope fixture attributes"""

from random import choice

import pytest

random_attribute_value = choice((42, "abc", None))


@pytest.fixture(scope="class", autouse=True)
def class_fixture(request):
    """Fixture to set class attribute"""
    request.cls.attribute = "initial"


@pytest.mark.usefixtures("class_fixture")
class TestWithClassScopeFixtureAttributes:
    """Test class with attributes set by function-scope fixtures"""

    def test_class_fixture_attribute_initial(self):
        """Test class scope fixture attribute at the beginning of the class"""
        assert self.attribute == "initial"

    def test_class_scope_fixture_attribute_recheck(self):
        """Test class scope fixture attribute after changing attribute value"""
        self.attribute = random_attribute_value  # type: ignore  # pylint: disable=attribute-defined-outside-init
        assert self.attribute == random_attribute_value

    def test_class_scope_fixture_attribute_forced_failure(self):
        """Test class scope fixture attribute to be forced failure"""
        assert False
