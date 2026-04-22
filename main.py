from typing import Annotated

import argplusplus as argpp
from argplusplus.command import Global
from argplusplus.parser import _class, flag

manager = argpp.manager.CommandManager("pyu")
manager.define_global(name="ea", flag=True)

@manager.register("example", "men", "are", "cool")
def ex(x: bool, y: int = 67):
    '''example'''
    print("x is", x, "y is", y)
    pass
   # print(manager.globals.ea)
  #  print("hi x:", x)


@manager.register("example", "men", "aremt")
def ex2(x: bool, y: int = 67):
    '''example2'''
    print("x is", x, "y is", y)
    pass
manager.process()