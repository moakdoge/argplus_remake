import argplusplus as argpp
from argplusplus.parser import _class, flag

manager = argpp.manager.CommandManager("example")


@manager.register("example", "command")
def example():
    print("works!!")
    
manager.process()