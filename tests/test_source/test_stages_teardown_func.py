"""This module contains class with failing tests at teardown stage (function)"""

import pytest


class TestFailInFunctionTeardown:
    """This test checks that the plugin correctly handles failure at teardown stage (function)"""

    @pytest.fixture(scope="function")
    def teardown(self, request):
        """
        Teardown method that always fails

        :param request: pytest request object
        :type request: _pytest.fixtures.FixtureRequest
        :return: None
        :rtype: None
        """

        def finalizer():
            """Finalizer that always fails"""
            assert False, "Teardown error"

        request.addfinalizer(finalizer)

    def test_teardown_pass(self, teardown):  # pylint: disable=unused-argument
        """This test should pass"""
        assert True

    def test_teardown_ignored(self):
        """This test should not run after teardown failure"""
        assert True
