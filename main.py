from configparser import ParsingError
from pathlib import Path
from typing import Annotated

import argplusplus as argpp
from argplusplus.command import Global
from argplusplus.command_context import CommandContext
from argplusplus.parser import _class, flag
from argplusplus.parser._alises import Alias
from argplusplus.parser.exceptions import ParsingException

manager = argpp.manager.CommandManager("pyu")
manager.define_global(name="ea", flag=True)



@manager.before("example men aremt")
def before(c: CommandContext):
    #c.replace(command="working", clear=True)
    print("command about to run:", " ".join(c.command.chain))
    #c.replace(args=(1241,), kwargs={})

@manager.after()
def after(c: CommandContext):
    print(c.args)
    print("command ran:", " ".join(c.command.chain), "with output:",c.output, "and successfully:", c.success, "and with exceptions of", c.exceptions)
    
@manager.catch(Exception)
def catch(err: Exception):
  #  print(err)
    return True


@manager.register("working")
def working():
    print("IT WORKED!!!")


   # print(manager.globals.ea)
  #  print("hi x:", x)


@manager.register("example", "men", "aremt")
def ex2(x: Annotated[str, Alias["long_path", "longer_path"]]):
    '''example2'''
    print("x is", x)

@manager.register("example")
def example(y: list[str]):
    print(manager.run("example", "men", "aremt", "67"))
    called = True


manager.process()