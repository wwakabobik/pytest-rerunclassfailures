"""Test class with function (params) attributes"""

from random import choice

random_attribute_value = choice((42, "abc", None))


class TestFunctionParamsAttributes:
    """Test class with function params attributes"""

    def test_function_params_attribute_initial(self, attribute="initial"):
        """Test function params attribute at the beginning of the class"""
        assert attribute == "initial"

    def test_function_params_attribute_recheck(self, attribute="initial"):
        """Test function params attribute after changing attribute value"""
        assert attribute == "initial"
        attribute = random_attribute_value
        assert attribute == random_attribute_value

    def test_function_params_attribute_forced_failure(self):
        """Test function params attribute to be forced failure"""
        assert False
