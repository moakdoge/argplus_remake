from difflib import get_close_matches
from typing import TYPE_CHECKING

from argplusplus.command import Command


if TYPE_CHECKING:
    from argplusplus.manager import CommandManager
    
class CommandSearcher:
    def __init__(self, manager: "CommandManager") -> None:
        self.manager = manager
        
    def search(self, chain: list[str] | tuple[str, ...]) -> Command | None:
        chain = tuple(chain)
        for command in self.commands:
            tupled_chain = tuple(command.chain)
            if tupled_chain == chain:
                return command
            
            for alias in command.spec.aliases:
                new = command.chain.copy()
                new[-1] = alias
                if tuple(new) == tuple(chain):
                    return command
                
    def search_partial(self, chain: list[str] | tuple[str, ...]) -> tuple[Command, ...] | None:
        chain = tuple(chain)
        commands: list[Command] = []
        for command in self.commands:
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
    
    def _suggest(self, name: str, options: list[str]) -> list[str] | None:
        matches = get_close_matches(name, options, n=3, cutoff=0.6)
        return matches if matches else None    
    
    def search_closest(self, chain: list[str], hidden: bool = False) -> list[str] | None:
        _options = set()
        for command in self.commands:
            if command.hidden and not hidden:
                continue
            _options.add(" ".join(command.chain))
            for ali in command.spec.aliases:
                cp = command.chain.copy()
                cp[-1] = ali
                _options.add(" ".join(command.chain[0:len(chain)]))
        return self._suggest(" ".join(chain), list(_options))
    
    
    @property
    def commands(self) -> list[Command]:
        return self.manager._real_cmds