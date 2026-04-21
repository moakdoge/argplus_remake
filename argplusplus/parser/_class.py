from functools import cached_property
import sys
from typing import Any

from .flag import Command, Argument
class Parser:
    def __init__(self, args: list[str] = sys.argv) -> None:
        self._raw_args = args
        self._keywords = []
        self._options = []
        for i, arg in enumerate(args[1:]):
            if arg.startswith("--"):
                self._options = args[1+i:]
                break
            self._keywords.append(arg)

        self._commands: list[Command] = [
            Command(["example", "one"], arguments=[
                Argument("x")
            ])
        ]
        valid: None | Command = None
        for cmd in self._commands:
            if cmd.parts == self._keywords:
                valid = cmd

        if valid is None:
            raise Exception
        self._options_tuple: list[tuple[str, Any]] = self._process_options(self._options, valid)


    def _process_options(self, opt: list[str], command: Command) -> list[tuple[str, Any]]:
        pairs = []
        arg_name: str = ""
        arg_value: str = ""

        for i, _o in enumerate(opt):
            if _o.startswith("--") and not "=" in _o:
                if len(opt)-1 == i:
                    arg_name = _o
                    arg_value = "True"
                else: 
                    nxt = opt[i+1]
                    if nxt.startswith("--"):
                        arg_name = _o
                        arg_value = nxt


            elif _o.startswith("--") and "=" in _o:
                sp = _o.split("=")
                arg_name, arg_value = sp[0], sp[1]
             #   pairs.append((sp[0], sp[1]))
            arg_name = arg_name.lstrip("-")
            _valid = False
            for _arg in command.arguments:
                if arg_name == _arg.name or arg_name in _arg.aliases:
                    pairs.append((arg_name, arg_value))
                    _valid = True

            if not _valid:
                raise Exception("Invalid argument!")
        return pairs
    
    @cached_property
    def caller(self):
        return self._raw_args[0]
    
    @cached_property
    def commands(self):
        return self._keywords