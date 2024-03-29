"""This module contains class with unpickable attributes"""

from io import TextIOWrapper

from socket import socket, AF_INET, SOCK_STREAM
from threading import Lock
from contextlib import contextmanager
import contextlib
from unittest.mock import Mock


class TestClassWithUnpickleableObject:  # pylint: disable=too-many-instance-attributes
    """Test class with unpickleable attributes"""

    @staticmethod
    def my_function() -> str:
        """
        Function for testing purposes

        :return: my_function
        :rtype: str
        """
        return "my_function"

    @contextmanager
    def my_context_manager():  # type:ignore  # pylint: disable=E0211
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
    function = my_function
    # Save original attributes to check them later
    ___original = {
        "unpickleable_attr": unpickleable_attr,
        "file": file,
        "sock": sock,
        "lock": lock,
        "generator": generator,
        "context_manager": context_manager,
        "custom_getattr": custom_getattr,
        "function": function,
    }

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
        assert hasattr(self.lock, "acquire") and callable(self.lock.acquire), "self.lock должен иметь метод acquire"
        assert isinstance(self.context_manager, contextlib._GeneratorContextManager)  # pylint: disable=W0212
        assert isinstance(self.custom_getattr, self.CustomGetattr)
        assert isinstance(self.function, type(self.my_function))
        # Check that the attributes are same
        assert self.file is self.___original["file"]
        assert self.sock is self.___original["sock"]
        assert self.lock is self.___original["lock"]
        assert self.generator is self.___original["generator"]
        assert self.context_manager is self.___original["context_manager"]

    def test_unpickleable_attributes_changed(self):
        """Test unpickleable attribute after changing attribute value"""
        # Change attributes
        self.unpickleable_attr = Mock()
        self.file = open(__file__, "r", encoding="utf-8")  # pylint: disable=consider-using-with
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.lock = Lock()
        self.generator = (i for i in range(10))
        self.context_manager = self.my_context_manager
        self.custom_getattr = self.CustomGetattr()
        self.function = self.my_function
        # Check attributes are updated
        assert self.unpickleable_attr is not self.___original["unpickleable_attr"]
        assert self.file is not self.___original["file"]
        assert self.sock is not self.___original["sock"]
        assert self.lock is not self.___original["lock"]
        assert self.generator is not self.___original["generator"]
        assert self.context_manager is not self.___original["context_manager"]

    def test_unpickleable_attributes_fail(self):
        """Test unpickleable attribute forced failure"""
        assert False
