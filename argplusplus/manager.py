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
        self._real_cmds: list[Command] = []
        self._globals: list[Global] = []
        self.globals = Globals()
        self.description = description
        
        pass

    def define_global(self, name: str, flag: bool = False, _type: type = type(Any)):
        self._globals.append(Global(
            name,
            _type=_type,
            flag=flag
        ))


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
            self._real_cmds.append(
                Command(func, list(commands), author=author, spec=c)
            )
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return func(*args, **kwargs)
            return wrapper
        return decorator


    def _usage(self, base: list[str] | tuple[str] | None = None):
        first_layer = set()
        chain: tuple[str, ...]
        chain_len: int = 0
        if base is None:
            for command in self._real_cmds:
                first_layer.add(command.chain[0])
                base = None
        else:
            chain = tuple(base)
            chain_len = len(chain)
            for command in self._real_cmds:
                if command.spec.parts[0:chain_len] != base: #checking for general match
                    continue

                if command.spec.parts != base: #check for full match
                    continue

                for argument in command.spec.arguments:
                    first_layer.add(argument.name)
                

        
        
        return f"Usage: {self.name}{(" " + " ".join(base)) if base else ""} [--help] {f'{{{" | ".join(list(first_layer))}}}' if len(first_layer) > 0 else ""}" # type: ignore
   
    
    
    def help(self, chain: list[str] | None = None):
        #get the first layer
        lines = [
            self._usage(chain), #generate the Usage: line
            self.description,
        ]
        command_strings: list[str] = []
        seen_commands: set[tuple[str, ...]] = set()
        spaces: int = 0

        if chain is None or len(chain) < 1:    
            max_len = max(len(i.spec.parts[0]) for i in self._real_cmds) * 2
            for command in self._real_cmds:
                
                primary = command.chain[0] #get the primary argument
                if primary in seen_commands:
                    continue

                seen_commands.add(primary)
            
                #caclulate space sizing
                spaces = max_len - len(primary)
                command_strings.append(f"\t{primary}")

            lines.extend([
                "commands:",
                *command_strings
            ])
        else:
            
            exact = False
            max_len = max(len(i.spec.parts[0]) for i in self._real_cmds) * 2
            chain_len = len(chain)

            for command in self._real_cmds:
                subset = list(command.spec.parts[0:chain_len])

                if subset != chain:
                    continue

                parts = command.spec.parts[chain_len:chain_len+1]
                if len(parts) < 1:
                    exact = True
                    for arg in command.spec.arguments:
                        spaces = max_len-len(arg.name)
                        command_strings.append(f"\t{arg.name} [{arg.tp.__name__}]{" "*spaces}'{arg.comment.strip("\n")}' {"(required)" if arg.default is _empty else f"(default: {arg.default})"}")
                else:
                    part_name = parts[0]
                    spaces = max_len - len(part_name)
                    command_strings.append(f"\t{part_name}{" "*spaces}")
        
            if len(command_strings) < 1:
                raise exceptions.InvalidCommmand(f"Command '{" ".join(chain)}' does not exist!") # type: ignore #type: ingore
            lines.extend([
                "commands:" if not exact else "options:",
                *command_strings
            ])
        return "\n".join(lines)
    
    def _find(self, chain: list[str] | tuple[str, ...]) -> Command | None:
        for command in self._real_cmds:
            if tuple(command.chain) == chain:
                return command
    
    def _process(self, args: list[str] | None = None) :
        args = args or sys.argv #get arguments

        self._main_parser = _class.Parser(args) #create core parser
        for glob in self._globals:
            self._main_parser._globals.append(
                flag.Argument(
                    glob.name,
                    ("",),
                    glob.flag,
                    glob._type or type[Any],
                    glob.default
                )
            )

        self._main_parser.add([i.spec for i in self._real_cmds])
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
        command = self._find(opt.cmd.parts)
        if command is None:
            print(self.help())
            return
        
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

    
    def process(self, args: list[str] | None = None):
        try:
            return self._process(args)
        except exceptions.ParsingException as e:
            print("error:", e)
            pass