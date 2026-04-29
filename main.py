#!/usr/bin/env python3
from configparser import ParsingError
from pathlib import Path
import threading
import time
from typing import Annotated, Any

import argplusplus as argpp
from argplusplus.command import Global
from argplusplus.command_context import CommandContext
from argplusplus.parser import _class, flag
from argplusplus.parser._alises import Alias
from argplusplus.parser.exceptions import ParsingException

manager = argpp.manager.CommandManager("pyu", make_executable=True)

@manager.register("example")
def example():
    '''hi world'''
    print("nope :3")

@manager.register("test")
def test():
    manager.run("example", stdout=False)
    print("stdout!")

@manager.after()
def after(context: CommandContext):
    print("output:", context.pipes.stdout)

manager.process()
