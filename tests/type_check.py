from typing import TYPE_CHECKING


if TYPE_CHECKING:
    class FixtureRequest:
        param: str
else:
    from typing import Any
    FixtureRequest = Any
