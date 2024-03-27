"""Test class with list type attributes"""

from random import choice

random_attribute_value = choice((42, "abc", None))


class TestListTypeAttributes:
    """Test class with list-type attributes"""

    attribute: list = ["initial"]

    def test_list_type_attribute_initial(self):
        """Test list type attribute at the beginning of the class"""
        assert len(self.attribute) == 1
        assert self.attribute[0] == "initial"

    def test_list_type_attribute_recheck(self):
        """Test list type attribute after changing attribute value"""
        self.attribute.append(random_attribute_value)
        assert len(self.attribute) == 2
        assert self.attribute[0] == "initial"
        assert self.attribute[1] == random_attribute_value

    def test_list_type_attribute_forced_failure(self):
        """Test list type attribute to be forced failure"""
        assert False
