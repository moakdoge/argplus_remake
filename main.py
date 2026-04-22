from typing import Annotated

import argplusplus as argpp
from argplusplus.parser import _class, flag

manager = argpp.manager.CommandManager("example")


@manager.register("package", "command")
def example(x: int, y: Annotated[int, "This is an argument"] = 1):
    '''
        Hi world!!! This is my docstring
    '''
    raise Exception
    pass

@manager.register("package", "command2")
def example3(x: str, y: int):
    '''Hi world!!!'''
    print("x is:", x, "y is:", y)
    pass


manager.process()