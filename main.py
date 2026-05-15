#!/usr/bin/env python3
from configparser import ParsingError
import json
from pathlib import Path
import sys
import textwrap
import threading
import time
from typing import Annotated, Literal, Optional

import argplusplus as argpp
from argplusplus.command import Global
from argplusplus.command_context import CommandContext
import argplusplus.console.color as clr
from argplusplus.parser import _class, flag
from argplusplus.parser._alises import Alias
from argplusplus.parser.exceptions import ParsingException

manager = argpp.manager.CommandManager("pyu", make_executable=True)

@manager.register("example")
def example(x):
    '''hi world'''
    
    print(x+4)
    
    
    
    
    print("x is", x)


manager.process()