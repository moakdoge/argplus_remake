from inspect import _empty
from typing import TYPE_CHECKING, Any

from argplusplus.command import Command
from argplusplus.parser import exceptions
from argplusplus.typingutils.co import clean_tp


if TYPE_CHECKING:
    from argplusplus.manager import CommandManager
class HelpModule:
    def __init__(self, manager: "CommandManager") -> None:
        self.manager: "CommandManager" = manager
    def usage(self, base: Command | list[str] | tuple[str] | None = None):
        base = self._chain(base)
        first_layer = set()
        chain: tuple[str, ...]
        if base is None:
            for command in self.manager._real_cmds:
                first_layer.add(command.chain[0])
                base = None
        else:
            chain = tuple(base)
            command = self.manager._find(chain)
            if command:     
                for argument in command.spec.arguments:
                    first_layer.add(argument.name)
            

        
        _globals = ["--"+i.name for i in self.manager._globals] 
        _globals_st = " | ".join(_globals)
        _cmd = f"{self.manager.name}{(" " + " ".join(base)) if base else ""}"
        return f"Usage: {_cmd} [{_globals_st}] {f'{{{" | ".join(list(first_layer))}}}' if len(first_layer) > 0 else ""}" # type: ignore
    def _chain(self, chain: Command | list[str] | tuple[str, ...] | None) -> list[str]:
        if chain is None:
            return []
        if isinstance(chain, Command):
            return list(chain.chain)
        return list(chain)
    
    def help(self, chain: Command | list[str] | None = None, show_hidden: bool = False):
        '''Returns the help text for a chain.'''
        #get the first layer
        chain = self._chain(chain)
        lines = [
            self.usage(chain), #generate the Usage: line
            self.manager.description,
        ]

        command_strings: list[str] = []
        seen_commands: set[tuple[str, ...]] = set()
        spaces: int = 0
        
        if chain is None or len(chain) < 1:    
            max_len = max(len(i.spec.parts[0]) for i in self.manager._real_cmds) * 2
            for command in self.manager._real_cmds:
                if command.hidden and not show_hidden:
                    continue
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
            max_len = max(len(i.spec.parts[0]) for i in self.manager._real_cmds) * 2
            chain_len = len(chain)
            command = self.manager._find(chain)
            seen = set()
            if not command:
                #raise exceptions.InvalidCommmand(f"Command '{" ".join(chain)}' does not exist!") 
                parts = []
                _found = self.manager._find_partial(chain)
                if not _found:
                    _close = self.manager._suggest_closest(chain, hidden=show_hidden)
                    if _close is not None and len(_close) > 0:
                        closest = self.manager._suggest_closest(chain, hidden=show_hidden)
                        
                        raise exceptions.InvalidCommmand(f"Command '{" ".join(chain)}' not found! Did you mean any of these: {", ".join(closest)}?") # type: ignore
                    else:
                        raise exceptions.InvalidCommmand(f"Command '{" ".join(chain)}' not found!")
                args = []
                for p in _found:
                    st = " ".join(p.chain[len(chain):len(chain)+1])
                    _a = []
                    spaces = max_len-len(st)
                    if len(chain)+1 >= len(p.chain):
                        for argument in p.spec.arguments:
                            _name = str(argument.name)
                            _a.append("{%s: %s (%s)}" % (_name,clean_tp(argument.tp),"required" if argument.default is _empty else "optional"))
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
                    command_strings.append(f"\t{arg.name}: {clean_tp(arg.tp)}{" "*spaces}'{arg.comment.strip("\n")}' {"(required)" if arg.default is _empty else f"(default: {arg.default})"}")
            else:
                part_name = parts[0]
                spaces = max_len - len(part_name)
                command_strings.append(f"\t{part_name}{" "*spaces}")
            if len(command_strings) < 1:
                command_strings.append("\tN/A")
            lines.extend([
                "commands:" if not exact else "options:",
                *command_strings
            ])

            if exact:
                lines.insert(1, "\n"+"'"+command.description+"'" if command is not None else "")
        return "\n".join(lines)
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.help(*args, **kwds)