from typing import Annotated, Generic, TypeAlias
from typing_extensions import Self


class _Flag:
    pass

Flag = Annotated[bool, _Flag()]