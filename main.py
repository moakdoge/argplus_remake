#!/usr/bin/env python3
import math
import random
import time

import argplusplus as argpp
from argplusplus import stringutils
from argplusplus.command_context import CommandContext
from argplusplus.types import Flag


manager = argpp.manager.CommandManager(name="pyu", make_executable=True)
render = manager.group("render", author="moakdoge")
input = manager.group("input", author="moakdoge")
    
@manager.catch(KeyboardInterrupt) # type: ignore
def catch(exp: KeyboardInterrupt):
    with manager.console.progress_bar(label="Reporting error") as spin:
        for i in range(50):
            var = random.random()
            sm = var * 0.1
            time.sleep(sm)
            spin.update(new=(i/49))
        spin.update(label="Reported error successfully.")
    return False
   # return True
    


@render.register()
def table():
    example_table = [[str(i) for i in range(8)] for i in range(10)]
    for x, _x in enumerate(example_table):
        l = [_ for _ in _x]
        lines = stringutils.space_evenly(*l, seperator_char="|")
        lines = stringutils.bar(lines)
        for l in lines[:]:
            lines.append("-"*len(l))
        lines.insert(0, "-"*len(lines[0]))
        print("\n".join(lines))
    
@input.register("confirm")
def confirm(prompt: str = "Would you like to download?", preferred: bool = True):
    answer = manager.console.confirm(prompt, preferred=preferred)
    manager.console.pprint(f"User answered: {"[green]yes[/green]" if answer else "[red]no[/red]"}")

@input.register("password")
def password(prompt: str = "Please type in a password > "):
    passwd = manager.console.password(prompt, censor="*")
    manager.console.pprint(f"User submitted: {passwd}")

@input.register("choice")
def choice(*opt: str, prompt: str = "Please choose an option", case_sensitive: Flag = False):
    chosen = manager.console.choice(opt, question=prompt, case_sensitive=case_sensitive)
    manager.console.pprint(f"User chose: [green]{chosen}[/green]")


@input.register("checkbox")
def checkbox():
    opt = manager.console.checkbox(["Option 1", "Option 2"])
    print(f"Chose: {opt}")
manager.process()