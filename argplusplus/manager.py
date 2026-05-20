from datetime import datetime
from pathlib import Path
from types import ModuleType
from argplusplus._tee import tee_output
from argplusplus.command_context import CommandContext, Pipes
from argplusplus.command_generator import CommandGenerator
from argplusplus.console import Console
from argplusplus.exception_hooker import ExceptionCatcher
from argplusplus.globals import Globals
from argplusplus.group import CommandGroup
from argplusplus.help import HelpException, HelpModule
from argplusplus.searcher import CommandSearcher
from argplusplus.terminal_properties import ManagerContext
from .command import Command, Global
from functools import cached_property, wraps
from typing import Annotated, Any, Optional, TypeVar, ParamSpec, Callable
from argplusplus.parser import flag, _class, exceptions
import inspect, os, stat, sys, tempfile

P = ParamSpec('P')
R = TypeVar('R')
class CommandManager:
    def __init__(self, name: str, *, description: str = "", make_executable: Annotated[bool, "Automatically adds a shabang to your file. AND runs chmod +x on it"] = False) -> None:
        self._main_parser: _class.Parser
        self.name = name
        self._command_tree = {}
        self._real_cmds: list[Command] = []
        self._globals: list[Global] = [
            Global("help", None, True, aliases=("h",)),
            Global("hidden", None, True, aliases=("hid",))
        ]
        self.generator: CommandGenerator = CommandGenerator(self)
        self.searcher: CommandSearcher = CommandSearcher(self)
        self.globals = Globals()
        self.help: HelpModule = HelpModule(self)
        self._exception_holder: list[ExceptionCatcher] = []
        self._before: list[Callable[[CommandContext]]] = []
        self._after: list[Callable[[CommandContext]]] = []
        self.description = description
        self.context: ManagerContext
        self.console: Console = Console()
        self._ready: list[Callable] = []

        if make_executable:
            self._chabang()
        
        pass

    def group(self, *commands: str, author: str | None = None) -> CommandGroup:
        grp = CommandGroup(commands, self, author=author)
        return grp
    
    def autogen(self, ob: object) -> list[Command]:
        '''Generates commands completely automatically'''
        commands: list[Command] = []
        if not hasattr(ob, "__dict__"):
            return commands

        owner = getattr(ob, "__name__", None) or ob.__class__.__name__
        for name, member in inspect.getmembers(ob):
            if name.startswith("_"):
                continue
            if not (inspect.isfunction(member) or inspect.ismethod(member) or inspect.isbuiltin(member)):
                continue

            try:
                inspect.signature(member)
            except (TypeError, ValueError):
                # Some builtins don't expose a signature; skip them.
                continue

            callable_member = member
            if inspect.ismethod(member) and member.__self__ is not None:
                sig = inspect.signature(member)
                params = list(sig.parameters.values())
                if params and params[0].name == "self":
                    def _bound(*args: Any, **kwargs: Any):
                        return member(*args, **kwargs)
                    _bound.__name__ = member.__name__
                    _bound.__doc__ = member.__doc__
                    _bound.__signature__ = sig.replace(parameters=params[1:]) # type: ignore
                    callable_member = _bound

            cmd = self.generator.process((name,), callable_member, author=owner)
            self._real_cmds.append(cmd)
            commands.append(cmd)
        return commands
    def ready(self, *, priority: float = 1) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return func(*args, **kwargs)
            func._pri = priority # type: ignore
            self._ready.append(func)
            return wrapper
        return decorator

    
    def _chabang(self):
        '''will AUTOMATICALLY add a chabang to whatever file this is run AND makes the file executable'''
        file: str | None = getattr(sys.modules['__main__'], '__file__', None)
        SHABANG = "#!/usr/bin/env python3"
        if file is None:
            raise FileNotFoundError(f"Couldn't find main file {file}")
        pathed = Path(file)
        with tempfile.NamedTemporaryFile("w", dir=pathed.parent, delete=True) as f:
            contents = ""
            with open(pathed, "r") as _:
                contents = _.read()
            if contents.startswith(SHABANG):
                return
            contents = SHABANG + "\n" + contents
            f.write(contents)
            f.flush()
            os.replace(Path(f.name), pathed)
        
        #makes it executable :3
        st = os.stat(pathed)
        os.chmod(pathed, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def define_global(self, name: str, *, flag: bool = False, _type: type = type(Any), aliases: list[str] | tuple[str, ...] | None = None):
        self._globals.append(Global(
            name,
            _type=_type,
            flag=flag,
            aliases=tuple(aliases) if aliases is not None else None
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

    def register(self, *commands: str, author: str="", aliases: tuple[str, ...] | None = None, hidden: bool = False) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            #start making a tree
            
            #simple input validation
            c = [_ for _ in commands if _.strip(" ").replace(" ", "") != ""]
            if len(c) <= 0:
                raise exceptions.InvalidCommmand(f"Command must not be blank!")
            
            _tmp_cmd = self.generator.process(tuple(c), func, aliases, author=author, hidden=hidden)
            self._real_cmds.append(_tmp_cmd)
            return func
        return decorator
    
    def root(self, *, author: Optional[str] = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return func(*args, **kwargs)
            _tmp = self.generator.process(("",), func, None)
            self._real_cmds.append(_tmp)
            return wrapper
        return decorator

                
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

    def _readied(self):
        if self._ready:
            self._ready.sort(key=lambda x: getattr(x, "_pri", 100)) # type: ignore
            for cmd in self._ready:
                cmd()
            self._ready = None # type: ignore
            
    def _process(self, args: list[str] | None = None, *, stdout: bool = True, stderr: bool = True) -> CommandContext | None:
        args = args or sys.argv #get arguments
        #process
        if not hasattr(self, "context"): #generate context
            self.context = ManagerContext(
                cwd=Path.cwd(),
                argv=args,
                start=datetime.now(),
                env=dict(os.environ),
            )
            self._readied()
            
        opt = None
        try:
            self._main_parser = _class.Parser(args) #create core parser
            self._main_parser._globals = self._create_globals()
            # Pre-scan flags so --help works even when parsing fails early.
            self._main_parser._mini_process_globals(args[1:])
            self._main_parser.add(self._specs)
            help = self._main_parser.processed_globals.get("help", False)
            
            try:
                opt = self._main_parser.process()
            except exceptions.MissingArgument:
                help = self._main_parser.processed_globals.get("help", False)
                if help:
                    raise HelpException
                raise
            
            
                
            if help:
                try:
                    self._main_parser.process()
                except Exception as e:
                    pass
                
                raise HelpException
                
            hidden = False
            if not opt:
                raise HelpException

            
            #handle globals
            for glob, val in self._main_parser.processed_globals.items():
                setattr(self.globals, glob, val)

            if self.globals.help:
                try:
                    self._main_parser.process()
                except Exception as e:
                    pass
                
                raise HelpException


            #look for command
            command = self.searcher.search(opt.cmd.parts)
            if command is None:
                raise HelpException

            _args, _kwrds = self.generator.gencall(command, opt.args)
            context = CommandContext(command, self, _args, _kwrds)
            try:
                for before in self._before:
                    before(context)
                #generate the pipes
                with tee_output(not stdout,not stderr) as (out, err):
                    output = context.command.function(*context.args, **context.kwargs)
                stdout_text, stderr_text = out.getvalue(), err.getvalue()
                pipes = Pipes(stderr=stderr_text, stdout=stdout_text)
                context.pipes, context.output, context.success = pipes, output, True
            except Exception as e:
                try:
                    o = self._raise(e)
                    if o:
                        context.exceptions.append(e)
                except Exception as e:
                    if isinstance(e, exceptions.ParsingException):
                        raise e
                    raise exceptions.ParsingException(e)
            
            for after in self._after:
                after(context)
            return context
        
        except HelpException as e:
            hidden = self._main_parser.processed_globals.get("hidden", False)
            help = self._main_parser.processed_globals.get("help", False)
            if opt is None:
                print(self.help(self._main_parser._keywords, show_hidden=hidden))
                return None
            
            if help:
                print(self.help(self._main_parser._keywords, show_hidden=hidden))

    
    def process(self, args: list[str] | None = None):

        try:
            return self._process(args)
        except exceptions.ParsingException as e:
           self.console.pprint(f"[red]{e}[/red]")
           self.quit(1)
           pass
        self.quit()



    def run(self, *commands: str, stdout: bool = True, stderr: bool = False) -> CommandContext | None:
        return self._process([f"{self.name}"]+list(commands), stdout=stdout, stderr=stderr)


    def quit(self, return_code: int = 0):
        sys.exit(return_code)

    @cached_property
    def _specs(self):
        return [i.spec for i in self._real_cmds]