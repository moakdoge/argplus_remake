from encodings import aliases
from inspect import Parameter
import inspect
from typing import TYPE_CHECKING, Annotated, Any, Callable, Optional, get_args, get_origin

from argplusplus.command import Command
from argplusplus.parser import flag, _empty
from argplusplus.parser._alises import Alias
from argplusplus.types import _Flag


if TYPE_CHECKING:
    from argplusplus.manager import CommandManager

class CommandGenerator:
    def __init__(self, manager: "CommandManager") -> None:
        self.manager: "CommandManager" = manager
    def _create_argument(self, arg: Parameter) -> flag.Argument:
        anno = arg.annotation if arg.annotation is not inspect._empty else _empty
        origin = get_origin(anno)
        comment = ""
        _flag = False
        _aliases = [""]
        if origin is Annotated:
            anno, comment = get_args(anno) 
            if isinstance(comment, Alias):
                _aliases = list(comment.args)
                comment = anno
            if isinstance(comment, _Flag):
                anno = bool              
                _flag = True     
                comment = ""    
        elif origin is Optional:
            anno = get_args(origin)[0]
        ver = arg.kind == arg.VAR_POSITIONAL
        return flag.Argument(
            arg.name,
            tuple(_aliases), # type: ignore
            _flag,
            anno, # type: ignore
            verradic=ver,
            default=arg.default if not arg.default is inspect._empty else _empty,
            comment=comment
        )
    def process(self, 
                commands: tuple[str, ...], 
                callable: Callable, 
                aliases: tuple[str, ...] | None = None, 
                author: str = "",
                hidden: bool = False
                ) -> Command:
        signature = inspect.signature(callable)
        arguments: list[flag.Argument] = []
        doc = callable.__doc__ if callable.__doc__ else ""
        for _, arg in signature.parameters.items():
            arguments.append(self._create_argument(arg))
        metadata =flag.CommandMetadata(
            parts=tuple(commands), 
            arguments=tuple(arguments), 
            comment=doc,
            aliases=aliases or ("",)
        )
        return Command(
            callable,
            author=author,
            spec=metadata,
            sig=signature,
            hidden=hidden
        )
    
    def gencall(self, command: Command, args: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
        sig = command.sig
        _kwrds = {}
        _args = []
        for name, param in sig.parameters.items():
            if name not in args:
                continue
            v = args[name]
            if param.kind == param.KEYWORD_ONLY:
                _kwrds[name] = v
            else:
                if isinstance(v, list):
                    _args.extend(v)
                else:
                    _args.append(v)
        return _args, _kwrds