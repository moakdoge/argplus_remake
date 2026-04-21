import argplusplus as argpp
from argplusplus.parser import _class, flag

manager = argpp.manager.CommandManager("example")


@manager.register("example", "command")
def example(*x: str, y: str):
    print(x, "y is:", y)
    pass


manager.process()