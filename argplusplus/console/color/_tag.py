from dataclasses import dataclass
import random
from typing import Self


@dataclass(slots=True)
class _Tag:
    raw: str
    name: str
    closing: bool
    start: int
    end: int
    content: str
    background: bool 
    @staticmethod
    def valid(input: str) -> bool:
        return True


@dataclass()
class _RandomTag(_Tag):
    _random_digits: int = 0
    
    @staticmethod
    def valid(input: str):
        return input.startswith("random:")

    def __post_init__(self):
        self.fix()
        
    def fix(self) -> Self:
        self._random_digits = int(self.name.lstrip("random:"))
        return self
    
    def get(self) -> str:
        dig = [str(random.randint(0, 9)) for i in range(self._random_digits)]
        return "".join(dig)
    
TAG_TYPES = _Tag.__subclasses__()


TAG_TYPES.append(_Tag)