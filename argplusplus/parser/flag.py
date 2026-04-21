from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, unsafe_hash=True)
class Argument:
    name: str = ""
    aliases: tuple[str] = () # type: ignore
    flag: bool = False
    tp: type = type[Any]
    def _convert_type(self, value: str):
        if self.flag:
            if value.lower() in ["y", "yes", "true"]:
                return True
            elif value.lower() in ["n", "no", "false"]:
                return False
            else:
                return bool(value)
        if self.tp == type[Any]:
            return self._coarse(value)
        return self.tp(value)
    
    def _coarse(self, value: str):
        _types = [int, float, bool]
        for t in _types:
            try:
                return t(value)
            except Exception as e:
                pass 
        raise ValueError

@dataclass(slots=True, unsafe_hash=True)
class Command:
    parts: tuple[str, ...]
    aliases: tuple[str, ...] = () # type: ignore
    arguments: tuple[Argument, ...] = () # type: ignore


@dataclass(frozen=True, slots=True)
class Result:
    cmd: Command
    args: dict[str, Any]