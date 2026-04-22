import argplusplus as argpp
from argplusplus.parser import _class, flag

manager = argpp.manager.CommandManager("example")


@manager.register("package", "command")
def example(x: int, y: int = 1):
    '''
        Hi world!!! This is my docstring
    '''
    print("x is:", x, "y is:", y)
    pass

@manager.register("package2", "command")
def example3(x: str, y: int):
    '''Hi world!!!'''
    print("x is:", x, "y is:", y)
    pass


manager.process()