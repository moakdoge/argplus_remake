from dataclasses import dataclass, field
from typing import Any

from argplusplus.typingutils.co import convert_value
from . import _empty

from .exceptions import *
from ._custom_bool import BoolPlus

@dataclass(slots=True, unsafe_hash=True)
class Argument:
    name: str = ""
    aliases: tuple[str, ...] = () # type: ignore
    flag: bool = False
    tp: type = type[Any]
    default: Any = _empty
    verradic: bool = False
    comment: str = ""

    def _convert_type(self, value: str):
        if self.flag:
            return BoolPlus.check(value)
        return convert_value(value, self.tp)

@dataclass(slots=True)
class CommandMetadata:
    parts: tuple[str, ...]
    aliases: tuple[str, ...] = () # type: ignore
    arguments: tuple[Argument, ...] = () # type: ignore
    comment: str = ""
    def __hash__(self) -> int:
        return hash((*self.parts, *self.aliases, *self.arguments, self.comment))


@dataclass(frozen=True, slots=True)
class Result:
    cmd: CommandMetadata
    args: dict[str, Any]