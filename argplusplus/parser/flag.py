from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Argument:
    name: str = ""
    aliases: list[str] = field(default_factory=list)
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
        if self.tp is type[Any]:
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

@dataclass(slots=True)
class Command:
    parts: list[str]
    aliases: list[str] = field(default_factory=list)
    arguments: list[Argument] = field(default_factory=list)