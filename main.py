#!/usr/bin/env python3
import math
import random
import time

import argplusplus as argpp
from argplusplus.command_context import CommandContext
from argplusplus.types import Flag


manager = argpp.manager.CommandManager(name="pyu", make_executable=True)
test_group = manager.group("example", author="moakdoge")

    
@manager.catch(Exception)
def catch(exp: Exception):
    with manager.console.progress_bar(label="Reporting error") as spin:
        for i in range(50):
            var = random.random()
            sm = var * 0.1
            time.sleep(sm)
            spin.update(new=(i/49))
        spin.update(label="Reported error successfully.")
    return False
   # return True
    
@manager.after()
def after(ctx: CommandContext):
    print(ctx.output)



@manager.root()
def x():
    print("oh well suprising")
    
manager.process()