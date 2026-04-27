from imaplib import Commands
import inspect
import sys

from argplusplus.command_context import CommandContext
from argplusplus.exception_hooker import ExceptionCatcher
from argplusplus.globals import Globals

from .command import Command, Global
import argparse
from functools import cached_property, wraps
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
        self._globals: list[Global] = [
            Global("help", None, True, aliases=("h",))
        ]
        self.globals = Globals()
        self._exception_holder: list[ExceptionCatcher] = []
        self._before: list[Callable[[CommandContext]]] = []
        self._after: list[Callable[[CommandContext]]] = []
        self.description = description
        
        pass

    def define_global(self, name: str, flag: bool = False, _type: type = type(Any)):
        self._globals.append(Global(
            name,
            _type=_type,
            flag=flag
        ))

    def catch(self, *exception_types: type[Exception]) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            self._exception_holder.append(ExceptionCatcher(
                func,tuple(exception_types)
            ))
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def before(self, *commands: str) -> Callable[[Callable[[CommandContext], R]], Callable[[CommandContext], R]]:
        def decorator(func: Callable[[CommandContext], R]) -> Callable[[CommandContext], R]:
            @wraps(func)
            def wrapper(context: CommandContext) -> R:
                if " ".join(context.command.chain) in commands or not commands:
                    return func(context)
                return None # type: ignore
            self._before.append(wrapper)
            return wrapper
        return decorator

    def after(self, *commands: str) -> Callable[[Callable[[CommandContext], R]], Callable[[CommandContext], R]]:
        def decorator(func: Callable[[CommandContext], R]) -> Callable[[CommandContext], R]:
            @wraps(func)
            def wrapper(context: CommandContext) -> R:
                if " ".join(context.command.chain) in commands or not commands:
                    return func(context)
                return None # type: ignore

            self._after.append(wrapper)
            return wrapper
        return decorator

    def register(self, *commands: str, author: str="", aliases: tuple[str, ...] | None = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
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
                    ("",), # type: ignore
                    (anno is bool),
                    anno, # type: ignore
                    verradic=ver,
                    default=arg.default if not arg.default is inspect._empty else _empty,
                    comment=comment
                )

                _args.append(a)

            c=flag.Command(parts=tuple(commands), arguments=tuple(_args), comment=func.__doc__ if func.__doc__ else "", aliases=aliases or ("", ))
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
        if base is None:
            for command in self._real_cmds:
                first_layer.add(command.chain[0])
                base = None
        else:
            chain = tuple(base)
            command = self._find(chain)
            if command:     
                for argument in command.spec.arguments:
                    first_layer.add(argument.name)
            

        
        _globals = ["--"+i.name for i in self._globals] 
        _globals_st = " | ".join(_globals)
        _cmd = f"{self.name}{(" " + " ".join(base)) if base else ""}"
        return f"Usage: {_cmd} [{_globals_st}] {f'{{{" | ".join(list(first_layer))}}}' if len(first_layer) > 0 else ""}" # type: ignore
   
    
    
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
            command = self._find(chain)
            seen = set()
            if not command:
                #raise exceptions.InvalidCommmand(f"Command '{" ".join(chain)}' does not exist!") 
                parts = []
                _found = self._find_partial(chain)
                if not _found:
                    raise exceptions.InvalidCommmand("Command not found!")
                args = []
                for p in _found:
                    st = " ".join(p.chain[len(chain):len(chain)+1])
                    _a = []
                    spaces = max_len-len(st)
                    if len(chain)+1 >= len(p.chain):
                        for argument in p.spec.arguments:
                            _name = str(argument.name)
                            _a.append("{%s: %s (%s)}" % (_name, argument.tp.__name__,"required" if argument.default is _empty else "optional"))
                        command_strings.append(f"\t{st}{" "*spaces}{"'%s'" % p.description} {f", ".join(_a)}")
                    else:
                        if not st in seen:
                            command_strings.append(f"\t{st}{" "*spaces}")
                            seen.add(st)
            else:
                parts = command.spec.parts[chain_len:chain_len+1]
                args = command.spec.arguments

            if len(parts) < 1:
                exact = True
                for arg in args:
                    spaces = max_len-len(arg.name)
                    command_strings.append(f"\t{arg.name} [{arg.tp.__name__}]{" "*spaces}'{arg.comment.strip("\n")}' {"(required)" if arg.default is _empty else f"(default: {arg.default})"}")
            else:
                part_name = parts[0]
                spaces = max_len - len(part_name)
                command_strings.append(f"\t{part_name}{" "*spaces}")

            lines.extend([
                "commands:" if not exact else "options:",
                *command_strings
            ])
        return "\n".join(lines)
    
    def _find(self, chain: list[str] | tuple[str, ...]) -> Command | None:
        chain = tuple(chain)
        for command in self._real_cmds:
            if tuple(command.chain) == chain:
                return command
            for alias in command.spec.aliases:
                new = list(command.chain.copy())
                new[-1] = alias
                if tuple(new) == tuple(chain):
                    return command
                
    def _find_partial(self, chain: list[str] | tuple[str, ...]) -> tuple[Command, ...] | None:
        chain = tuple(chain)
        commands: list[Command] = []
        for command in self._real_cmds:
            if tuple(command.chain)[0:len(chain)] == chain:
                commands.append(command)
                continue
            for alias in command.spec.aliases:
                new = list(command.chain.copy())
                new[-1] = alias
                if tuple(new)[0:len(chain)] == tuple(chain):
                    commands.append(command)
                    break
        return tuple(commands)
                
    def _create_globals(self) -> list[flag.Argument]:
        _global_list: list[flag.Argument] = []
        for glob in self._globals:
            _global_list.append(
                flag.Argument(
                    glob.name,
                    glob.aliases or ("",), # type: ignore
                    glob.flag,
                    glob._type or type[Any],
                    glob.default
                )
            )
        return _global_list
    
    def _raise(self, exc: Exception) -> bool:
        success = False
        for i in self._exception_holder:
            
            if type(exc) in i.exception_type or Exception in i.exception_type:
                success = i.function(exc) or False

        if not success:
            raise exc
        return success

    
    def _process(self, args: list[str] | None = None) :
        args = args or sys.argv #get arguments

        self._main_parser = _class.Parser(args) #create core parser
        self._main_parser._globals = self._create_globals()
        self._main_parser.add(self._specs)
        
        #process
        opt = self._main_parser.process()

        if not opt:
            print(self.help(self._main_parser._keywords))
            return

        
        #handle globals
        for glob, val in self._main_parser.processed_globals.items():
            setattr(self.globals, glob, val)

        if self.globals.help:
            try:
                self._main_parser.process()
            except Exception as e:
                pass
            
            print(self.help(self._main_parser._keywords))
            return

        #look for command
        command = self._find(opt.cmd.parts)
        if command is None:
            print(self.help())
            return
        
        _args = []
        _kwrds = {}

        sig = inspect.signature(command.function)
        for a, v in opt.args.items():
            if a in sig.parameters:
                arg = sig.parameters[a]
                if arg.kind == arg.KEYWORD_ONLY:
                    _kwrds[a] = v
                else:
                    if isinstance(v, list):
                        _args.extend(v)
                    else:
                        _args.append(v)


        context = CommandContext(command, self, _args, _kwrds)
        try:
            for before in self._before:
                before(context)
            output = context.command.function(*context.args, **context.kwargs)
            context.output = output
            context.success = True
        except Exception as e:
            o = self._raise(e)
            if o:
                context.exceptions.append(e)
        for after in self._after:
            after(context)

    def process(self, args: list[str] | None = None):
        try:
            return self._process(args)
        except exceptions.ParsingException as e:
            print("error:", e)

    def run(self, *commands: str):
        self._process([f"{self.name}"]+list(commands))

    @cached_property
    def _specs(self):
        return [i.spec for i in self._real_cmds]