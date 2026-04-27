from pathlib import Path
from typing import Annotated

import argplusplus as argpp
from argplusplus.command import Global
from argplusplus.command_context import CommandContext
from argplusplus.parser import _class, flag

manager = argpp.manager.CommandManager("pyu")
manager.define_global(name="ea", flag=True)



@manager.before("example men aremt")
def before(c: CommandContext):
    #c.replace(command="working", clear=True)
    print("command about to run:", " ".join(c.command.chain))
    #c.replace(args=(1241,), kwargs={})

@manager.after()
def after(c: CommandContext):
    print("command ran:", " ".join(c.command.chain), "with output:",c.output, "and successfully:", c.success, "and with exceptions of", c.exceptions)
    
@manager.catch(Exception)
def catch(err: Exception):
    print(err)
    return True


@manager.register("working")
def working():
    print("IT WORKED!!!")

@manager.register("example")
def ex(k: Path):
    if not k.exists():
        raise FileNotFoundError("...")
    print(k.absolute())

   # print(manager.globals.ea)
  #  print("hi x:", x)


@manager.register("example", "men", "aremt")
def ex2(*x: str):
    '''example2'''
    print("x is", x)


manager.process()