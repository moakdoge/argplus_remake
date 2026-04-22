from typing import Annotated

import argplusplus as argpp
from argplusplus.command import Global
from argplusplus.parser import _class, flag

manager = argpp.manager.CommandManager("example")
manager._globals.append(Global("ea"))

@manager.register("example")
def ex(x: int = 0):
    print(manager.globals.ea)
    print("hi x:", x)


manager.process()