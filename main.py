#!/usr/bin/env python3
import random
import time

import argplusplus as argpp
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
    
@test_group.register("hi")
def hi(x: Flag, y: bool, z: bool):
    '''wow'''
    print("wow, x is", x, "y is", y, "z is", z)
manager.process()