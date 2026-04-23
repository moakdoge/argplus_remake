from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from argplusplus.command import Command
from argplusplus.parser.flag import Argument


if TYPE_CHECKING:
    from . import manager
@dataclass(slots=True)
class CommandContext:
    command: Command
    manager: "manager.CommandManager"
    args: list[Any]
    kwargs: dict[str, Any]
    output: Any = None
    success: bool = False
    exceptions: list[Exception] = field(default_factory=list)


    def replace(self,*,command: list[str] | tuple[str, ...] | None = None, args: list[Any] | tuple[Any] | None = None, kwargs: dict[str, Any] | None = None):
        if isinstance(command, tuple):
            command = [*command]

        if args is not None:
            self.args = list(args)
        if kwargs is not None:
            self.kwargs = kwargs
        
        if command is not None:
            self.command = self.manager._find(list(command)) # type: ignore
        