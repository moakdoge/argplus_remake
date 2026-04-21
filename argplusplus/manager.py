import inspect
import sys

from .command import Command
import argparse
from functools import wraps
from typing import TypeVar, ParamSpec, Callable
P = ParamSpec('P')
R = TypeVar('R')
from argplusplus.parser import flag, _class, _empty
class CommandManager:
    def __init__(self, name: str, description: str = "N/A") -> None:
        self._main_parser: _class.Parser
        self.name = name
        self._command_tree = {}
        self._tmp_cmds: list[flag.Command] = []
        self._real_cmds: list[Command] = []
        
        pass


    def register(self, *commands: str, author: str="") -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            #start making a tree
            last = self._command_tree
            sig = inspect.signature(func)
            _args = []
            
            for st, arg in sig.parameters.items():
                anno = arg.annotation if arg.annotation is not inspect._empty else _empty
                ver = arg.kind == arg.VAR_POSITIONAL
                a = flag.Argument(
                    arg.name,
                    ("",),
                    (anno is bool),
                    anno,
                    verradic=ver
                )
                _args.append(a)

            c=flag.Command(parts=tuple(commands), arguments=tuple(_args))
            self._tmp_cmds.append(
                c
            )
            self._real_cmds.append(
                Command(func, list(commands), author=author, command=c)
            )
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def process(self, args: list[str] | None = None) :
        if args is None:
            args = sys.argv

        self._main_parser = _class.Parser(args)
        self._main_parser.add(self._tmp_cmds)
        opt = self._main_parser.process()
        
        #look for command
        for command in self._real_cmds:
            if tuple(command.chain) == opt.cmd.parts:
                _args = []
                _kwrds = {}
                for a, v in opt.args.items():
                    if isinstance(v, list):
                        _args.extend(v)
                    else:
                        _kwrds[a] = v
                command.function(*_args, **_kwrds)