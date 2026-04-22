from typing import Annotated

import argplusplus as argpp
from argplusplus.command import Global
from argplusplus.parser import _class, flag

manager = argpp.manager.CommandManager("pyu")
manager.define_global(name="ea", flag=True)

@manager.register("example", "men")
def ex(x: bool, y: int = 67):
    '''example'''
    print(manager.globals)
    pass
   # print(manager.globals.ea)
  #  print("hi x:", x)


manager.process()