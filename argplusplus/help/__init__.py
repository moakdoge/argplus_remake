from argplusplus.parser.flag import _empty
from typing import TYPE_CHECKING, Any
from collections.abc import Iterable


from argplusplus.command import Command
from argplusplus.parser import exceptions
from argplusplus.parser.flag import Argument
from argplusplus.typingutils.co import clean_tp


if TYPE_CHECKING:
    from argplusplus.manager import CommandManager
class HelpModule:
    def __init__(self, manager: "CommandManager") -> None:
        self.manager: "CommandManager" = manager
        self.searcher = self.manager.searcher
    def usage(self, base: Command | list[str] | tuple[str] | None = None):
        base = self._chain(base)
        first_layer = set()
        chain: tuple[str, ...]
        author = ""
        if base is None:
            for command in self.manager._real_cmds:
                first_layer.add(command.chain[0])
                base = None
        else:
            chain = tuple(base)
            command = self.searcher.search(chain)
            if command:     
                for argument in command.spec.arguments:
                    first_layer.add(argument.name)
                author = f"(by {command.author})"
            

        
        _globals = ["--"+i.name for i in self.manager._globals] 
        _globals_st = " | ".join(_globals)
        _cmd = f"{self.manager.name}{(" " + " ".join(base)) if base else ""}"
        return f"Usage: {_cmd} [{_globals_st}] {f'{{{" | ".join(list(first_layer))}}}' if len(first_layer) > 0 else ""}{author}" # type: ignore
    
    def _chain(self, chain: Command | list[str] | tuple[str, ...] | None) -> list[str]:
        if chain is None:
            return []
        if isinstance(chain, Command):
            return list(chain.chain)
        return list(chain)
    
    def _get_longest(self, commands: list[Command] | Iterable) -> int:
        '''Gets the longest part.'''
        if isinstance(commands, Iterable) and not isinstance(commands, list):
            return max(commands)
        return max(len(i.spec.parts[0]) if len(i.spec.parts) > 0 else 0 for i in commands)
    
    def _get_visible_commands(self, show_hidden: bool = False) -> list[Command]:
        _cmds: list[Command] = []
        seen = set()
        for command in self.manager._real_cmds:
            if command.hidden and not show_hidden:
                continue
            if len(command.chain) <= 0:
                continue
            primary = command.chain[0] #get the primary argument
            if primary in seen:
                continue
            seen.add(primary)
            _cmds.append(command)
        return _cmds
    
    def _find_command(self, chain: list[str], show_hidden: bool = False) -> tuple[Command, ...]:
        #raise exceptions.InvalidCommmand(f"Command '{" ".join(chain)}' does not exist!") 
        _found = self.searcher.search_partial(chain)
        if not _found:
            _close = self.searcher.search_similar(chain, hidden=show_hidden)
            if _close is not None and len(_close) > 0:
                closest = self.searcher.search_similar(chain, hidden=show_hidden)
                raise exceptions.InvalidCommmand(f"Command '{" ".join(chain)}' not found! Did you mean any of these: {", ".join(closest)}?") # type: ignore
            else:
                raise exceptions.InvalidCommmand(f"Command '{" ".join(chain)}' not found!")
        return _found
    
    def _process_arg(self, arg: Argument, full: bool = False, spaces: int = 0) -> str:
        '''Converts an arg to a property formatted arg'''
        
        name = str(arg.name)
        required = (arg.default is _empty)
        print()
        _type = clean_tp(arg.tp)
        comment = arg.comment.strip("\n")
        required_comment = "required" if required else "optional"
        
        if not full:
            return "{%s: %s (%s)}" % (name
                                    ,_type,
                                    required_comment)
            
        if not required_comment:
            required_comment = f"default: {str(arg.default)}"
        return f"\t{name}: {_type}{" "*spaces}'{comment}' ({required_comment})"
        
    def help(self, chain: Command | list[str] | None = None, show_hidden: bool = False):
        '''Returns the help text for a chain.'''
        #get the first layer
        chain = self._chain(chain)
        lines = [
            self.usage(chain), #generate the Usage: line
            self.manager.description,
        ]

        if len(self.manager._real_cmds) < 1: #NO COMMANDS :(
            raise exceptions.InvalidCommmand(f"No commands have been registered!")
        
        max_len: int = self._get_longest(self.manager._real_cmds) * 2
        command_strings: list[str] = []
        spaces: int = 0
        chain_len: int = len(chain)
        
        #If we haven't provided a chain at all; for example, `app --help`
        if chain is None or len(chain) < 1:    
            for command in self._get_visible_commands(show_hidden):
                primary = command.chain[0]
                spaces = max_len - len(primary)
                command_strings.append(f"\t{primary}")


            lines.extend([
                "commands:",
                *command_strings
            ])
            
            if len(command_strings) < 1:
                lines.append("\tNo commands were found. ")
                
            return "\n".join(lines)

        #so we are calling it on a real command or group, like `app example --help`
        exact = False
        command = self.searcher.search(chain)
        seen = set()
        parts = []
        if not command: #oh noes we never found a command :0
            _found = self._find_command(chain, show_hidden=True)
            args = []
            for cmd in _found: # all found choices
                prefix = " ".join(cmd.chain[chain_len:chain_len+1]) #Get the rest after the found parts
                spaces = max_len - len(prefix)
                if len(chain)+1 >= len(cmd.chain): # meaning that this is a full command
                    _args = [self._process_arg(arg) for arg in cmd.spec.arguments]
                    command_strings.append(f"\t{prefix}{" "*spaces}{"'%s'" % cmd.description} {f", ".join(_args)}")
                else: #category / sub
                    if not prefix in seen:
                        command_strings.append(f"\t{prefix}{" "*spaces}")
                        seen.add(prefix)
        else: # we just found a command meaning it's like `app example command --help`
            parts = command.spec.parts[chain_len:chain_len+1]
            args = command.spec.arguments

        if len(parts) < 1: # meaning we found a command
            exact = True
            for arg in args:
                spaces = max_len-len(arg.name)
                command_strings.append(self._process_arg(arg, full=True, spaces=spaces))
        else: #awww, no command found :(
            part_name = parts[0]
            spaces = max_len - len(part_name)
            command_strings.append(f"\t{part_name}{" "*spaces}")
            
        if len(command_strings) < 1: # If a category doesn't have any commands OR a command has no args
            command_strings.append("\tNo commands were found.")
        
        lines.extend([
            "commands:" if not exact else "options:",
            *command_strings
        ])

        if exact:
            lines.insert(1, "\n"+"'"+command.description+"'" if command is not None else "") # Insert the description if it can find the command
            
        return "\n".join(lines)
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.help(*args, **kwds)
        
class HelpException(Exception):
    pass