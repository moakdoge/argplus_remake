from functools import cached_property
from itertools import takewhile
import sys
from typing import Any, Iterable, get_origin
from . import _empty
from .flag import CommandMetadata, Argument, Result
from .exceptions import *
class Parser:
    def __init__(self, args: list[str] = sys.argv) -> None:
        self._raw_args = args
        self._globals: list[Argument] = []
        self.processed_globals: dict[str, Any] = {}
        self._commands: set[CommandMetadata] = set()
    def _negative_number(self, s: str) -> bool:
        try:
            float(s)
            return s.startswith("-")
        except ValueError:
            return False
    def process(self) -> Result | None:
        args = self._raw_args
        self._keywords = []
        self._options = []
        for i, arg in enumerate(args[1:]):
            dashes = len(arg) - len(arg.lstrip("-"))
            is_option = arg.startswith("-") and not self._negative_number(arg) and (dashes == 2 or dashes == 1)
            if is_option:
                self._options = args[1 + i :]
                break
            self._keywords.append(arg)
        self._mini_process_globals(self._options)


        valid: None | CommandMetadata = None
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
        #print(self._options)
        new = []
        arg_index = 0
        seen = set()
        #required = [i.name for i in valid.arguments if i.default is _empty and not i.flag]
        for val in fx:
            while arg_index < len(valid.arguments) and valid.arguments[arg_index].flag:
                arg_index += 1
            if arg_index >= len(valid.arguments):
                raise InvalidArgument(
                    f"Too many parameters! Expected: {len(valid.arguments)}, got: {len(new) + 1}"
                )

            current = valid.arguments[arg_index]
            new.append(f"--{current.name}={val}")
            seen.add(current.name)
            if current.verradic:
                continue
            arg_index += 1
        

        merged_options = list(self._options)
        merged_options.extend(new)
        self._options_tuple = self._process_options(merged_options, valid)
        return Result(
            valid,self._options_tuple
        )
    
    def add(self, *commands: CommandMetadata | list[CommandMetadata] | tuple[CommandMetadata] | set[CommandMetadata]):
        for command in commands:
            if isinstance(command, (list, tuple, set)):
                for cmd in command:
                    self._commands.add(cmd)
            else:
                self._commands.add(command)


    def _enumerate_options(self, opt: list[str]):
        for i, option in enumerate(opt):
            arg_name = option
            arg_value = ""
            flag = False
            if not option.startswith("-"): #so NOT an argument; just move on
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
            yield arg_name, arg_value, flag
    
    def _mini_process_globals(self, opt: list[str]):
        '''Used exclusively for flag globals bc they can be processed later on'''
        for glob in self._globals:
            if not glob.flag:
                continue
            st = [f"--{glob.name}", f"-{glob.name}"]

            found = any(s for s in st if s in opt)
            if found:
                self.processed_globals[glob.name] = True
                continue
                
            p1 = [f"-{a}" for a in glob.aliases]
            p2 = [f"--{a}" for a in glob.aliases]
            combined = p1 + p2
            found_aliases = any(_ for _ in combined if _ in opt)
            if found_aliases:
                self.processed_globals[glob.name] = True
                continue
            self.processed_globals[glob.name] = False
            
    def _process_globals(self, opt: list[str], command: CommandMetadata | None = None):
        '''Returns found globals'''
        for arg_name, arg_value, flag in self._enumerate_options(opt):
            argument: Argument | None = None
            if command is not None:
                for _arg in command.arguments:
                    if arg_name == _arg.name or arg_name in _arg.aliases:
                        arg_name = _arg.name
                        argument = _arg

            if argument is None: #try to find it in globals instead
                for glob in self._globals:
                    glob_name = glob.name.lstrip("-")
                    if glob_name == arg_name or arg_name in glob.aliases:
                        self.processed_globals[glob_name] = glob._convert_type(arg_value)
                        break
    
                        
    def _process_options(self, opt: list[str], command: CommandMetadata) -> dict[str, Any]:
        self._process_globals(opt, command)
        pairs = []
        arg_name: str = ""
        arg_value: str = ""
        seen = set()
        vals: dict[str, list] = {}
        
        #preprocess the args to make it easier to handle  
        
        #attempt to recover the args if they're at the start
        for arg_name, arg_value, flag in self._enumerate_options(opt):
            #find applicable argument
            argument: Argument | None = None
            for _arg in command.arguments:
                if arg_name == _arg.name or arg_name in _arg.aliases:
                    arg_name = _arg.name
                    argument = _arg

            if argument is None: #try to find it in globals instead
                for glob in self._globals:
                    glob_name = glob.name.lstrip("-")
                    if glob_name == arg_name or arg_name in glob.aliases:
                        self.processed_globals[glob_name] = glob._convert_type(arg_value)
                        break
                else: #success
                    #attempt to split the arg
                    nms = [arg.name for arg in command.arguments]
                    ls=list(arg_name)
                    result = list(set(nms) & set(ls))
                    if len(result) == len(ls): #short-flag match
                        for arg in command.arguments:
                            if arg.name not in result:
                                continue
                            
                            if not arg.flag:
                                raise InvalidArgument(f"Argument {arg.name} is not a flag! To use shortform, please make it a flag!")
                            pairs.append((arg.name, True))
                        continue
                    raise InvalidArgument(f"Argument --{arg_name} is invalid!")
                continue

            if not argument.flag and flag:
                raise ValueError("Must be marked as flag!")
            if get_origin(argument.tp) in (list, tuple):
                if not arg_name in vals: #if its not found just default to []
                    vals.setdefault(arg_name, [])
                vals[arg_name].append(argument._convert_type(arg_value))
            elif not argument.verradic: #checking for a normal variable
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
            if arg.name in vals:
                new[arg.name] = vals[arg.name]
            if not arg.name in new:
                if arg.default is not _empty:
                    new[arg.name] = arg.default
                elif arg.flag:
                    new[arg.name] = False
                else:
                    raise MissingArgument(f"Missing parameter '{arg.name}'")

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
    