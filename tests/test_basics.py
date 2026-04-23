import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argplusplus as argpp
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
    
