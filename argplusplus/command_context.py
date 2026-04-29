from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Annotated, Any
from argplusplus.command import Command
from argplusplus.parser.flag import Argument
from io import StringIO

if TYPE_CHECKING:
    from . import manager

@dataclass(slots=True, frozen=True)
class Pipes:
    stdout: str
    stderr: str
@dataclass(slots=True)
class CommandContext:
    command: Command
    manager: "manager.CommandManager"
    args: list[Any]
    kwargs: dict[str, Any]
    output: Any = None
    success: bool = False
    pipes: Pipes = Pipes("", "")
    exceptions: list[Exception] = field(default_factory=list)


    def replace(self,*,
                command: str | list[str] | tuple[str, ...] | None = None, 
                args: list[Any] | tuple[Any] | None = None, 
                kwargs: dict[str, Any] | None = None,
                clear: Annotated[bool, "Removes all existing args and kwargs"] = False
                ):
        if isinstance(command, tuple):
            command = [*command]
        if isinstance(command, str):
            command = command.split(" ")
        if clear:
            self.args = []
            self.kwargs = {}
        if args is not None:
            self.args = list(args)
        if kwargs is not None:
            self.kwargs = kwargs
        
        if command is not None:
            self.command = self.manager._find(list(command)) # type: ignore
        