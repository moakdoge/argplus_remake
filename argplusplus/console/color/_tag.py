from dataclasses import dataclass
import random
import re
from typing import Any, Self
from urllib.parse import urlparse
import uuid


@dataclass(slots=True)
class _Tag:
    raw: str
    name: str
    closing: bool
    start: int
    end: int
    content: str
    background: bool 
    _format: bool = False
    @classmethod
    def valid(cls, input: str) -> bool:
        return True
    def get(self, closing: str | None = None) -> str | tuple[str, str]:
        '''DO NOT USE'''
        raise NotImplemented


@dataclass()
class _BaseTag(_Tag):
    command: str = ""
    _format: bool = False
    @classmethod
    def valid(cls, input: str) -> bool:
        if cls is _BaseTag:
            return False
        return input.startswith(cls.command)
    def __post_init__(self):
        self.name = self.name.removeprefix(self.command)
    def get(self, closing: str | None = None) -> str | tuple[str, str]:
        raise NotImplemented

@dataclass()
class _RandomTag(_BaseTag):
    command = "?random:"
    _random_digits: int = 0
    
    def __post_init__(self):
        self._random_digits = int(self.name.removeprefix(self.command))
    
    def get(self, closing: str | None = None) -> str:
        dig = [str(random.randint(0, 9)) for i in range(self._random_digits)]
        return "".join(dig) # type: ignore
    
from datetime import datetime
@dataclass()
class _DateTag(_BaseTag):
    command = "?now"
    _format_type: str = ""
    
    @classmethod
    def valid(cls, input: str):
        if not input.startswith("?now"):
            return False
        try:
            v = datetime.now()
            l = v.strftime(input) 
        except Exception as e:
            return False
        return True
    
    def __post_init__(self):
        self._format_type = self.name.removeprefix("?now:")
    
    def get(self, closing: str | None = None) -> str:
        if self._format_type.strip(" ") == "":
            return f"{datetime.now().isoformat()}"
        return f"{datetime.now().strftime(self._format_type)}"
    


VARIABLES: dict[str, str] = {
}

@dataclass()
class _AssignVariable(_BaseTag):
    command = "$"
    _format_type: str = ""
    
    @classmethod
    def valid(cls, input: str):
        if input.startswith("$") and ":" in input:
            return True
        return False
    
    def __post_init__(self):
        import argplusplus.console.color as clr
        global VARIABLES
        e = self.name.removeprefix("$")
        name, value = e.split(":")
        VARIABLES[name] = clr.process_tags(str(value))

    
    def get(self, closing: str | None = None) -> str:
        return ""
    


@dataclass
class _Variable(_BaseTag):
    command = "$"
    def __post_init__(self):
        self._name = self.name.removeprefix("$")
        
    
    def get(self, closing: str | None = None) -> str:
        if self._name in VARIABLES:
            return VARIABLES[self._name]
        raise AttributeError(f"Variable {self._name} doesnt exist")
    


class _Subin():
    def __init__(self, val: str):
        self.value = val


@dataclass
class _Upper(_BaseTag):
    command = "upper"
    def get(self, closing: str | None = None) -> tuple[str, str]:
        if closing is None:
            return "", ""
        return ("", closing.upper()) # type: ignore
    
@dataclass
class _UUID4(_BaseTag):
    command = "uuid"
    def get(self, closing: str | None = None) -> tuple[str, str]:
        return (str(uuid.uuid4()), "") # type: ignore
@dataclass
class _Lower(_BaseTag):
    command = "lower"
    def get(self, closing: str | None = None) -> tuple[str, str]:
        if closing is None:
            return "", ""
        return ("", closing.lower()) # type: ignore
    
URL_REGEX = re.compile(
    r'^(https?:\/\/)'          # scheme
    r'(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})'  # domain
    r'(:\d+)?'                 # optional port
    r'(\/[^\s]*)?$'            # path
)
@dataclass
class _Url(_BaseTag):
    command: str = "link"
    _format: bool = True
    @classmethod
    def valid(cls, input: str) -> bool:
        return super().valid(input)

    def get(self, closing: str | None = None) -> tuple[str, str]:
        if closing:
            return "", f"[underline][blue]\033]8;;{closing}\033\\{closing}\033]8;;\033\\[/underline][/blue]"
        return "", ""

TAG_TYPES: list[type[_BaseTag]] = _BaseTag.__subclasses__()
TAG_TYPES.append(_Tag) # type: ignore
