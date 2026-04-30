#!/usr/bin/env python3
from configparser import ParsingError
import json
from pathlib import Path
import sys
import textwrap
import threading
import time
from typing import Annotated, Any

import argplusplus as argpp
from argplusplus.command import Global
from argplusplus.command_context import CommandContext
import argplusplus.console.color as clr
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
    with manager.console.progress_bar(label="Installing packages..") as progress:
        for i, pack in enumerate(sys.modules):
            st=manager.console.pprint(f"[red]Installing {pack}[/red]")
            progress.update(label=st,new=i/(len(sys.modules)-1))
            time.sleep(0.1)

@manager.register("work")
def work(t: str = ''):
    if t == '':
        t = '''It is currently [if:[@gt:[?now:%H]:12]][@sub:[?now:%H]:12]:[?now:%M]:[?now:%S] pm[/if][if:[@eq:[?now:%H]:12]]12:[?now:%M]:[?now:%S] pm[/if][if:[@lt:[?now:%H]:12]][?now:%H]:[?now:%M]:[?now:%S] am[/if]'''
    manager.console.pprint(" ".join(textwrap.dedent(t).split()))

manager.process()
