import argplusplus as argpp
from argplusplus.parser import _class, flag

manager = argpp.manager.CommandManager("example")


@manager.register("example", "command")
def example(x: int = 9):
    #lmao
    print("works!! x is", x)

manager.process()