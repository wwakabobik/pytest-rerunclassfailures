"""Type hints for fixtures and tests"""

from typing import TYPE_CHECKING


if TYPE_CHECKING:

    class FixtureRequest:  # pylint: disable=too-few-public-methods
        """Fixture request object typing stub"""

        param: str

else:
    from typing import Any

    FixtureRequest = Any
