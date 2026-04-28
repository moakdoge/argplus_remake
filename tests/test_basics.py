import datetime
import time
from typing import Annotated

import pytest
import sys
from pathlib import Path



sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argplusplus as argpp
from argplusplus.parser._alises import Alias
@pytest.fixture
def manage():
    return argpp.manager.CommandManager("test")


### REAL TESTS ###

def test_basic_command(manage, capsys):
    called = False
    @manage.register("example")
    def example():
        nonlocal called
        assert True
        called = True

    manage.run("example")
    assert "error" not in capsys.readouterr().out
    assert called is True


def test_basic_command_with_defaults(manage, capsys):
    called = False
    @manage.register("example")
    def example(x: int = 0):
        nonlocal called
        assert x==0
        called = True

    manage.run("example")
    assert "error" not in capsys.readouterr().out
    assert called is True

def test_basic_command_with_defaults_overrided(manage, capsys):
    called = False
    @manage.register("example")
    def example(x: int = 0):
        nonlocal called
        assert x==4
        called = True

    manage.run("example", "--x=4")
    assert "error" not in capsys.readouterr().out
    assert called is True

    
def test_basic_command_with_all_arg_types(manage, capsys):
    called = 0
    @manage.register("example")
    def example(x: int):
        nonlocal called
        assert x == 4
        called += 1
        

    manage.run("example", "4")
    manage.run("example", "--x", "4")
    manage.run("example", "--x=4")
    assert "error" not in capsys.readouterr().out
    assert called == 3

def test_basic_command_with_kwds(manage, capsys):
    called = False
    @manage.register("example")
    def example(x: int = 0, *, y: int):
        nonlocal called
        assert x==-4
        assert y==12
        called = True

    manage.run("example", "-4", "--y=12")
    assert "error" not in capsys.readouterr().out
    assert called is True

def test_basic_command_with_verradics(manage, capsys):
    called = False
    @manage.register("example")
    def example(*x: str):
        nonlocal called
        assert x == ("big", "string")
        called = True

    manage.run("example", "big", "string")
    assert "error" not in capsys.readouterr().out
    assert called is True

def test_basic_command_with_verradics_and_kwargs(manage, capsys):
    called = False
    @manage.register("example")
    def example(*x: str, y: int = 0):
        nonlocal called
        assert x == ("big", "string")
        assert y == 69
        called = True

    manage.run("example", "big", "string", "--y=69")
    assert "error" not in capsys.readouterr().out
    assert called is True

def test_basic_command_with_verradics_and_kwargs_and_args(manage, capsys):
    called = False
    @manage.register("example")
    def example(normal: int, *x: str, y: int = 0):
        nonlocal called
        assert normal == 52
        assert x == ("big", "string")
        assert y == 69
        called = True

    manage.run("example","52", "big", "string", "--y=69")
    assert "error" not in capsys.readouterr().out
    assert called is True
    
def test_basic_command_with_aliases(manage, capsys):
    called = False
    @manage.register("exampl22e", aliases=("e",))
    def example(y: Annotated[int, Alias["new"]] = 0):
        nonlocal called
        assert y == 69
        called = True

    manage.run("e", "--new", "69")
    assert "error" not in capsys.readouterr().out
    assert called is True
    

def test_basic_command_with_aliases_and_lists(manage, capsys):
    called = False
    @manage.register("exampl22e", aliases=("e",))
    def example(y: list[int]):
        nonlocal called
        assert len(y) == 4 and y[1] == 69
        called = True

    manage.run("e", "0,69,0,0")
    assert "error" not in capsys.readouterr().out
    assert called is True
    

def test_basic_threaded(manage, capsys):
    called = False
    @manage.register("exampl22e", aliases=("e",))
    def example():
        nonlocal called
        time.sleep(0.25)
        called = True

    o=manage.run("e",threaded=True)
    o.join()
    assert manage.context.runtime > datetime.timedelta(seconds=0.2)
    assert called is True

def test_basic_time(manage, capsys):
    @manage.register("test")
    def example(x: int):
        return x
    
    def test():
        manage.run("test", "--x=123")

    from timeit import timeit

    tm=0
    tests = 1e4
    for i in range(int(tests)):
        start = time.perf_counter_ns()
        manage.run("test", "--x=123")
        tm += (time.perf_counter_ns() - start)
    tm /= tests
    assert tm <= 50_000 #50us / 0.000005s max time to run command