from typing import Annotated

import argplusplus as argpp
from argplusplus.command import Global
from argplusplus.command_context import CommandContext
from argplusplus.parser import _class, flag

manager = argpp.manager.CommandManager("pyu")
manager.define_global(name="ea", flag=True)



@manager.before()
def before(c: CommandContext):
    print("command about to run:", " ".join(c.command.chain))
    c.replace("example", "men", "aremt", args=[1])

@manager.after()
def after(c: CommandContext):
    print("command ran:", " ".join(c.command.chain), "with output:",c.output, "and successfully:", c.success, "and with exceptions of", c.exceptions)
    
@manager.catch(TypeError)
def catch(err: TypeError):
    print(err)
    return True


@manager.register("working")
def working():
    print("IT WORKED!!!")

@manager.register("example", "men", "are", "cool")
def ex():
    '''example'''
    raise TypeError("hi")
    
   # print(manager.globals.ea)
  #  print("hi x:", x)


@manager.register("example", "men", "aremt")
def ex2(x: bool, *, y: int = 67):
    '''example2'''
    print("x is", x, "y is", y)
   # manager.run("example", "men", "are", "cool")
    pass

manager.process()