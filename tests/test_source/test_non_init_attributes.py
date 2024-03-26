"""Test class with static attributes"""

from random import choice

random_attribute_value = choice((42, "abc", None))


class TestWithNonInitAttributes:
    """Test class with static attributes"""

    attribute = "initial"

    def test_non_init_attribute_initial(self):
        """Test non-init attribute at the beginning of the class"""
        assert self.attribute == "initial"

    def test_non_init_attribute_recheck(self):
        """Test non-init attribute after changing attribute value"""
        self.attribute = random_attribute_value
        assert self.attribute == random_attribute_value

    def test_non_init_attribute_forced_failure(self):
        """Test non-init attribute to be forced failure"""
        assert False
