from dataclasses import dataclass
from functools import cached_property
from typing import Callable


@dataclass(frozen=True)
class Command:
    function: Callable
    author: str = "N/A"
    
    @cached_property
    def description(self):
        if self.function.__doc__:
            return self.function.__doc__
    