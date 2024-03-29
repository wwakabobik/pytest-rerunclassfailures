"""This module contains class with failing tests at teardown stage (class), full pass, without aborting"""

import pytest


class TestFailInClassTeardownPure:
    """This test checks that the plugin correctly handles failure at teardown stage (class)"""

    @pytest.fixture(autouse=True)
    def class_teardown(self, request):
        """
        Teardown method that always fails

        :param request: pytest request object
        :type request: _pytest.fixtures.FixtureRequest
        :return: None
        :rtype: None
        """

        def finalizer():
            """Finalizer that always fails"""
            assert False, "Class teardown error"

        request.addfinalizer(finalizer)

    def test_teardown_pass(self):
        """This test should pass"""
        assert True
