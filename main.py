#!/usr/bin/env python3
import math
import random
import time

import argplusplus as argpp
from argplusplus import stringutils
from argplusplus.command_context import CommandContext
from argplusplus.console.tui.core import TUI
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
    opt = manager.console.checkbox({"Option 1": False, "Option 2": True})
    print(f"Chose: {opt}")
    
@manager.root()
def tui():
    obj = TUI(manager.console) \
    .title("Settings") \
    .checkbox(label="Create .gitignore", checked=True, key="gitignore") \
    .checkbox(label="Save Raw", key="saveraw") \
    .spacer() \
    .button(label="file explorer test", callback=lambda z: z.file_explorer("~", key="path")) \
    .button(label="test", callback=lambda z: z.message_box("test", key="wowzers")) \
    .title(label="Other") \
    .choice(label="Compiler Optimization",options=["-O", "-O2", "-O3"], key="comp_opt") \
    .submenu(label="Properties", menu=lambda tui: (
        tui
        .title("Properties") 
        .textbox("Name", key="name")
        .checkbox("Modern", key="modern")
        .password("Secret", key="secret")

    ), key="properties")  \
    .slider("Percent to build at once", transform="percent") \
    .spacer() \
    .bar() \
    .button(label="Build", callback=lambda tui: (
       tui
       .title("Are you sure you want to build?")
       .paragraph("Building may take over 10 minutes. Please make sure to not power off or unplug your PC. To see more, check [link]https://google.com[/link]")
        .button("YES", callback=lambda t: (
            t.title("Built successfully!") 
            .button("Back", callback=lambda t: t.back(2))
            .button("Exit", lambda t: t.full_exit())
        ))
        .button("NO", callback=lambda t: t.back(1))

    )) 

    obj.build()
    
    values = obj.get_values()
    manager.console.print(str(values))
    
manager.process()