import inspect
import sys

from .command import Command
import argparse
from functools import wraps
from typing import TypeVar, ParamSpec, Callable
P = ParamSpec('P')
R = TypeVar('R')
from argplusplus.parser import flag, _class
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
                a = flag.Argument(
                    arg.name,
                    ("",),
                    (arg.annotation is bool),
                    arg.annotation
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
                command.function(**opt.args)