from functools import cached_property
import sys
from typing import Any

from .flag import Command, Argument, Result
class Parser:
    def __init__(self, args: list[str] = sys.argv) -> None:
        self._raw_args = args
        self._commands: set[Command] = set()

    def process(self) -> Result:
        args = self._raw_args
        self._keywords = []
        self._options = []
        for i, arg in enumerate(args[1:]):
            if arg.startswith("--"):
                self._options = args[1+i:]
                break
            self._keywords.append(arg)

        valid: None | Command = None
        for cmd in self._commands:
            if list(cmd.parts) == self._keywords:
                valid = cmd

        if valid is None:
            raise Exception
        self._options_tuple: dict[str, Any] = self._process_options(self._options, valid)
        return Result(
            valid,self._options_tuple
        )
    
    def add(self, *commands: Command | list[Command] | tuple[Command] | set[Command]):
        for command in commands:
            if isinstance(command, (list, tuple, set)):
                for cmd in command:
                    self._commands.add(cmd)
            else:
                self._commands.add(command)


    def _process_options(self, opt: list[str], command: Command) -> dict[str, Any]:
        pairs = []
        arg_name: str = ""
        arg_value: str = ""

        for i, _o in enumerate(opt):
            arg_name = _o
            flag = False
            if not _o.startswith("--"):
                continue
            if _o.startswith("--") and not "=" in _o:
                if len(opt)-1 == i:
                    arg_name = _o
                    arg_value = "True"
                    flag = True
                else: 
                    nxt = opt[i+1]
                    arg_name = _o
                    arg_value = nxt
            elif _o.startswith("--") and "=" in _o:
                sp = _o.split("=")
                arg_name, arg_value = sp[0], sp[1]

            arg_name = arg_name.lstrip("-")
            _valid = False
            for _arg in command.arguments:
                if arg_name == _arg.name or arg_name in _arg.aliases:
                    if _arg.flag is False and flag is True:
                        raise ValueError("Must be marked as flag!")
                    pairs.append((arg_name, _arg._convert_type(arg_value)))
                    _valid = True

            if not _valid:
                raise Exception("Invalid argument!")
            
        n = {}
        for p, x in pairs:
            n[p] = x
        
        return n
    
    @cached_property
    def caller(self):
        return self._raw_args[0]
    
    @property
    def commands(self):
        return self._commands
    