#!/usr/bin/env python3
import random
import time

import argplusplus as argpp

manager = argpp.manager.CommandManager(name="pyu", make_executable=True)

@manager.ready(priority=1)
def on_ready():
    print("should be first")
    pass
    
@manager.ready(priority=2)
def on_ready2():
    print("should be second")
    pass
    
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
    
@manager.register("hi")
def hi():
    raise FileNotFoundError("nope")

manager.process()