from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, TypeVar, ParamSpec, Callable

P = ParamSpec('P')
R = TypeVar('R')


if TYPE_CHECKING:
    from argplusplus.manager import CommandManager
    
@dataclass()
class CommandGroup:
    commands: tuple[str, ...] | str | list[str]
    manager: "CommandManager"
    author: str | None = None
    def __post_init__(self):
        '''Why i do it this way i dont fucking know'''
        if isinstance(self.commands, str):
            self.commands = self.commands.split(" ")
        self.commands = list(self.commands)
        self._registered: list[tuple[tuple[str, ...], Callable]] = []
    
    def register(self, *commands: str, author: str | None = None, aliases: tuple[str, ...] = (), hidden: bool = False) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            expanded: list[str] = list(self.commands[:])
            expanded.extend(list(commands))
            self._registered.append((commands, func))
            self.manager.register(*expanded, author=author or self.author or "", aliases=aliases,hidden=hidden)(func)
            return func
        return decorator    
    