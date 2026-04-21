from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Argument:
    name: str = ""
    aliases: list[str] = field(default_factory=list)
    tp: type = type[Any]

@dataclass(slots=True)
class Command:
    parts: list[str]
    aliases: list[str] = field(default_factory=list)
    arguments: list[Argument] = field(default_factory=list)