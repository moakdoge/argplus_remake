from imaplib import Commands
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
    def __init__(self, name: str, description: str = "") -> None:
        self._main_parser: _class.Parser
        self.name = name
        self._command_tree = {}
        self._tmp_cmds: list[flag.Command] = []
        self._real_cmds: list[Command] = []
        self.description = description
        
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
                    anno, # type: ignore
                    verradic=ver
                )
                _args.append(a)

            c=flag.Command(parts=tuple(commands), arguments=tuple(_args), comment=func.__doc__ if func.__doc__ else "")
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


    def _usage(self, base: list[str] | None = None):
        first_layer = set()
        if base is None:
            for command in self._real_cmds:
                first_layer.add(command.chain[0])
                base = [command.chain[0]]
        else:

            for command in self._real_cmds:
                if command.chain[0:len(base)] == base:
                    first_layer.add(command.chain[len(base)])
    
        return f"Usage: {self.name} {" ".join(base)} [-h] {{{" | ".join(list(first_layer))}}}" # type: ignore
    def help(self, chain: list[str] | None = None):
        #get the first layer
        first_layer = set()
        for command in self._real_cmds:
            first_layer.add(command.chain[0])

        lines = [
            self._usage(chain),
            self.description,
        ]
        
        if True:
            
            cmds = []
            ln = max(len(i.parts[0]) for i in self._tmp_cmds) * 2
            for command in self._tmp_cmds:
                cmds.append(f"\t{command.parts[0]}{" "*(ln-len(command.parts[0]))}{command.comment.strip("\n")}")
            lines.extend([
                "commands:",
                *cmds
            ])
        return "\n".join(lines)
    
    def process(self, args: list[str] | None = None) :
        if args is None:
            args = sys.argv

        self._main_parser = _class.Parser(args)
        self._main_parser.add(self._tmp_cmds)
        opt = self._main_parser.process()
        if not opt:
            print(self.help())
            return
        
        success = False
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
                success = True
        if not success:
            print(self.help())