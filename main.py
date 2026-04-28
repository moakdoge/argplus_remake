from configparser import ParsingError
from pathlib import Path
import threading
import time
from typing import Annotated

import argplusplus as argpp
from argplusplus.command import Global
from argplusplus.command_context import CommandContext
from argplusplus.parser import _class, flag
from argplusplus.parser._alises import Alias
from argplusplus.parser.exceptions import ParsingException

manager = argpp.manager.CommandManager("pyu")
manager.define_global(name="ea", flag=True)

@manager.register("example")
def example():
    time.sleep(0.5)

@manager.register("test")
def test():
    t = manager.run("example", threaded=True)
    if isinstance(t, threading.Thread):
        print('wow..')
        t.join()
        print('bye')

manager.process()
