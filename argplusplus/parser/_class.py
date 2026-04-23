from functools import cached_property
import sys
from typing import Any
from . import _empty
from .flag import Command, Argument, Result
from .exceptions import *
class Parser:
    def __init__(self, args: list[str] = sys.argv) -> None:
        self._raw_args = args
        self._globals: list[Argument] = []
        self.processed_globals: dict[str, Any] = {}
        self._commands: set[Command] = set()

    def process(self) -> Result | None:
        args = self._raw_args
        self._keywords = []
        self._options = []
        for i, arg in enumerate(args[1:]):
            if arg.startswith("-") and (len(arg) - len(arg.lstrip("-")) == 2):
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
                continue
            for alias in cmd.aliases:
                parts = list(cmd.parts).copy()
                parts[-1] = alias
                if self._keywords[:len(parts)] == parts:
                    if len(parts) > valid_len:
                        valid = cmd
                        valid_len = len(parts)




        if valid is None:
            return None
        

        fx = self._keywords[valid_len:]
        new = []
        i=0
        for val in enumerate(fx):
            if i >= len(valid.arguments):
                raise InvalidArgument(f"Too many parameters! Expected: {len(valid.arguments)}, got: {i+1}")
            new.append(f"-{valid.arguments[i].name}={val[1]}")
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

        for i, option in enumerate(opt):
            arg_name = option
            flag = False
            if not option.startswith("-"): #so NOT an argument; just move on
                _current_legit_arg += 1
                continue

            
            #attempt to get arg name and arg value
            if option.startswith("-") and not "=" in option: #format: -x 12
                if len(opt)-1 == i:
                    arg_name = option
                    arg_value = "True"
                    flag = True
                else: 
                    nxt = opt[i+1]
                    arg_value = nxt

            elif option.startswith("-") and "=" in option: #format: -x=12
                sp = option.split("=")
                arg_name, arg_value = sp[0], sp[1]
            arg_name = arg_name.lstrip("-")

            #find applicable argument
            argument: Argument | None = None
            for _arg in command.arguments:
                if arg_name == _arg.name or arg_name in _arg.aliases:
                    argument = _arg

            if argument is None: #try to find it in globals instead
                for glob in self._globals:
                    glob_name = glob.name.lstrip("-")
                    if glob_name == arg_name or arg_name in glob.aliases:
                        self.processed_globals[glob_name] = glob._convert_type(arg_value)
                        break
                else: #success
                    raise InvalidArgument("Invalid argument!")
                continue



            if not argument.flag and flag:
                raise ValueError("Must be marked as flag!")
            
            if not argument.verradic: #checking for a normal variable
                if arg_name in seen:
                    raise InvalidArgument(f"Please only use {arg_name} once!") 
                seen.add(arg_name)
                pairs.append((arg_name, argument._convert_type(arg_value)))
            else: #checking for verradic (*x)
                if not arg_name in vals: #if its not found just default to []
                    vals.setdefault(arg_name, [])
                vals[arg_name].append(argument._convert_type(arg_value))

            


        new = dict(pairs)
        for arg in command.arguments:
            if not arg.name in new:
                if arg.default is not _empty:
                    new[arg.name] = arg.default
                elif arg.flag:
                    new[arg.name] = False
                else:
                    raise InvalidArgument(f"Missing parameter '{arg.name}'")

        #fix globals
        for glob in self._globals:
            if not glob.name in self.processed_globals:
                self.processed_globals[glob.name] = glob.default if not glob.flag else False
        new.update(vals)
        return new
    
    @cached_property
    def caller(self):
        return self._raw_args[0]
    
    @property
    def commands(self):
        return self._commands
    