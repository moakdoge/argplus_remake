from imaplib import Commands
import inspect
import sys

from argplusplus.globals import Globals

from .command import Command, Global
import argparse
from functools import wraps
from typing import Annotated, Any, TypeVar, ParamSpec, Callable, get_args, get_origin
P = ParamSpec('P')
R = TypeVar('R')
from argplusplus.parser import flag, _class, _empty, exceptions
class CommandManager:
    def __init__(self, name: str, description: str = "") -> None:
        self._main_parser: _class.Parser
        self.name = name
        self._command_tree = {}
        self._tmp_cmds: list[flag.Command] = []
        self._real_cmds: list[Command] = []
        self._globals: list[Global] = []
        self.globals = Globals()
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
                comment = ""
                if get_origin(anno) is Annotated:
                    anno, comment = get_args(anno) 

                ver = arg.kind == arg.VAR_POSITIONAL
                a = flag.Argument(
                    arg.name,
                    ("",),
                    (anno is bool),
                    anno, # type: ignore
                    verradic=ver,
                    default=arg.default if not arg.default is inspect._empty else _empty,
                    comment=comment
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
                base = None
        else:
       
            for command in self._tmp_cmds:
                if list(command.parts[0:len(base)]) == base:
                    if list(command.parts) == base:
                        _ = []
                        for a in command.arguments:
                            first_layer.add(a.name)
                        continue
                    #first_layer.add(list(command.parts[len(base)]))
        
        
        return f"Usage: {self.name}{(" " + " ".join(base)) if base else ""} [--help] {f'{{{" | ".join(list(first_layer))}}}' if len(first_layer) > 0 else ""}" # type: ignore
    def help(self, chain: list[str] | None = None):
        #get the first layer
        lines = [
            self._usage(chain),
            self.description,
        ]
        
        if chain is None or len(chain) < 1:
            
            cmds = []
            seen = set()
            ln = max(len(i.parts[0]) for i in self._tmp_cmds) * 2
            for command in self._tmp_cmds:
                if command.parts[0] in seen:
                    continue
                seen.add(command.parts[0])
                cmds.append(f"\t{command.parts[0]}{" "*(ln-len(command.parts[0]))}")

            lines.extend([
                "commands:",
                *cmds
            ])
        else:
            
            cmds = []
            exact = False
            ln = max(len(i.parts[0]) for i in self._tmp_cmds) * 2
            for command in self._tmp_cmds:
                if list(command.parts[0:len(chain)]) == chain:
                    if list(command.parts) == chain:
                        exact = True
                        for arg in command.arguments:
                            cmds.append(f"\t{arg.name} [{arg.tp.__name__}]{" "*(ln-len(arg.name))}'{arg.comment.strip("\n")}' {"(required)" if arg.default is _empty else f"(default: {arg.default})"}")
                    else:
                        cmds.append(f"\t{command.parts[len(chain):len(chain)+1][0]}{" "*(ln-len(command.parts[len(chain):len(chain)+1]))}")
           
            if len(cmds) < 1:
                raise exceptions.InvalidCommmand(f"Command '{" ".join(chain)}' does not exist!") # type: ignore #type: ingore
            lines.extend([
                "commands:" if not exact else "options:",
                *cmds
            ])
        return "\n".join(lines)
    
    def _process(self, args: list[str] | None = None) :
        args = args or sys.argv

        self._main_parser = _class.Parser(args)
        for i in self._globals:
            self._main_parser._globals.append(
                flag.Argument(
                    i.name,
                    ("",),
                    False,
                    i._type or type[Any]
                )
            )

        self._main_parser.add(self._tmp_cmds)
        #programming globals
        if "--help" in self._main_parser._raw_args:
            try:
                self._main_parser.process()
            except Exception as e:
                pass
            print(self.help(self._main_parser._keywords))
            return
        

        opt = self._main_parser.process()

        if not opt:
            print(self.help(self._main_parser._keywords))
            return

        
        #handle globals
        for glob, val in self._main_parser.processed_globals.items():
            setattr(self.globals, glob, val)


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
                try:
                    command.function(*_args, **_kwrds)
                except TypeError as e:
                    raise exceptions.MissingArgument(f"Missing argument: {e}")
                success = True
        if not success:
            print(self.help())
    
    def process(self, args: list[str] | None = None):
        try:
            return self._process(args)
        except exceptions.ParsingException as e:
            print("error:", e)
            pass