"""This module contains class with unpickable attributes"""

from io import TextIOWrapper

from socket import socket, AF_INET, SOCK_STREAM
from threading import Lock
from contextlib import contextmanager
import contextlib
from unittest.mock import Mock


class TestClassWithUnpickleableObject:
    """Test class with unpickleable attributes"""

    @contextmanager
    def my_context_manager():
        """Context manager for testing purposes"""
        yield "context_manager"

    class CustomGetattr:  # pylint: disable=R0903
        """Custom __getattr__ for testing purposes"""

        def __getattr__(self, item):
            """
            Custom __getattr__ for testing purposes

            :param item: some item
            :type item: Any
            :return: None
            :rtype: None
            :raises AttributeError: Custom __getattr__ for {item}
            """
            raise AttributeError(f"Custom __getattr__ for {item}")

    unpickleable_attr = Mock()
    unpickleable_attr.__deepcopy__ = Mock(side_effect=TypeError("cannot deepcopy this object"))
    file = open(__file__, "r", encoding="utf-8")  # pylint: disable=R1732
    sock = socket(AF_INET, SOCK_STREAM)
    lock = Lock()
    generator = (i for i in range(10))
    context_manager = my_context_manager()
    custom_getattr = CustomGetattr()

    def __del__(self):
        """Close file and socket when object is deleted"""
        self.file.close()
        self.sock.close()

    def test_unpickleable_attributes_initial(self):
        """Test unpickleable attribute at the beginning of the class"""
        # Check that the attributes is not None
        assert self.unpickleable_attr is not None
        assert self.file is not None
        assert self.sock is not None
        assert self.lock is not None
        assert self.generator is not None
        assert self.context_manager is not None
        assert self.custom_getattr is not None
        # Type wasn't changed
        assert isinstance(self.unpickleable_attr, Mock)
        assert isinstance(self.file, TextIOWrapper)
        assert isinstance(self.sock, socket)
        #assert isinstance(self.lock, Lock)  # pylint: disable=W1116
        assert isinstance(self.context_manager, contextlib._GeneratorContextManager)  # pylint: disable=W0212
        assert isinstance(self.custom_getattr, self.CustomGetattr)

    def test_unpickleable_attributes_fail(self):
        """Test unpickleable attribute forced failure"""
        assert False
