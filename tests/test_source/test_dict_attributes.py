"""Test class with dict type attributes"""

from random import choice

random_attribute_value = choice((42, "abc", None))


class TestDictTypeAttributes:
    """Test class with dict-type attributes"""

    attribute: dict = {"initial": "initial_value"}

    def test_list_type_attribute_initial(self):
        """Test dict type  at the beginning of the class"""
        assert len(self.attribute.keys()) == 1
        assert "initial" in self.attribute
        assert self.attribute["initial"] == "initial_value"

    def test_list_type_attribute_recheck(self):
        """Test dict type after changing attribute value"""
        self.attribute["secondary"] = random_attribute_value
        assert len(self.attribute.keys()) == 2
        assert self.attribute["initial"] == "initial_value"
        assert self.attribute["secondary"] == random_attribute_value

    def test_dict_type_attribute_forced_failure(self):
        """Test dict type attribute to be forced failure"""
        assert False
