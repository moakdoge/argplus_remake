from functools import cached_property
import sys
from typing import Any
from . import _empty
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
        valid_len = -1

        for cmd in self._commands:
            parts = list(cmd.parts)
            if self._keywords[:len(parts)] == parts:
                if len(parts) > valid_len:
                    valid = cmd
                    valid_len = len(parts)



        if valid is None:
            raise Exception
        

        fx = self._keywords[valid_len:]
        new = []
        i=0
        for val in enumerate(fx):
            new.append(f"--{valid.arguments[i].name}={val[1]}")
            if valid.arguments[i].verradic:
                continue
            i+=1

        self._options = new + self._options

        
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
        _current_legit_arg = 0
        seen = set()
        vals: dict[str, list] = {}
        #attempt to recover the args if they're at the staert

        for i, _o in enumerate(opt):
            arg_name = _o
            flag = False

            if not _o.startswith("--"):
                #pairs.append((command.arguments[_current_legit_arg].name, _o))
                _current_legit_arg += 1
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
                    
                    if not _arg.verradic:
                        if arg_name in seen:
                            raise Exception(f"Please only use {arg_name} once")
                        seen.add(arg_name)
                        pairs.append((arg_name, _arg._convert_type(arg_value)))
                    else:

                        if not arg_name in vals:
                            vals.setdefault(arg_name, [])
                        vals[arg_name].append(_arg._convert_type(arg_value))
                    _valid = True

            if not _valid:
                raise Exception("Invalid argument!")
            
        n = {}
        for p, x in pairs:
            n[p] = x
        for arg in command.arguments:
            if not arg.name in n:
                if arg.default is not _empty:
                    n[arg.name] = arg.default
                elif arg.flag:
                    n[arg.name] = False

        n.update(vals)
        return n
    
    @cached_property
    def caller(self):
        return self._raw_args[0]
    
    @property
    def commands(self):
        return self._commands
    