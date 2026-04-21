import argparse
from dataclasses import dataclass, field
from functools import cached_property
from typing import Callable


@dataclass()
class Command:
    function: Callable
    chain: list
    author: str = "N/A"
    children: dict[str, "Command"] = field(default_factory=dict)
    parser: argparse.ArgumentParser | None = None

    @cached_property
    def description(self):
        if self.function.__doc__:
            return self.function.__doc__
    
    def __repr__(self) -> str:
        return f"<command ({",".join(self.chain)}: {self.parser})"