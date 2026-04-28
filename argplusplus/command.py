import argparse
from dataclasses import dataclass, field
from functools import cached_property
import inspect
from typing import Any, Callable

from argplusplus.parser import flag, _empty


@dataclass()
class Command:
    function: Callable
    chain: list
    spec: flag.Command
    sig: inspect.Signature
    author: str = "N/A"
    children: dict[str, "Command"] = field(default_factory=dict)
    
    @cached_property
    def description(self):
        if self.function.__doc__:
            return self.function.__doc__
        return ""
    
    def __repr__(self) -> str:
        return f"<command ({",".join(self.chain)})>"
    
@dataclass(frozen=True, slots=True)
class Global:
    name: str
    _type: type | None = None
    flag: bool = False
    default: Any = _empty
    aliases: tuple[str, ...] | None = None