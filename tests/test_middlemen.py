import pytest
import sys
from pathlib import Path

from argplusplus.command_context import CommandContext

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argplusplus as argpp
@pytest.fixture
def manage():
    return argpp.manager.CommandManager("test")


### REAL TESTS ###

def test_before_hook(manage, capsys):
    called = False
    intercepted = ""

    @manage.before()
    def d(c: CommandContext):
        nonlocal intercepted
        c.replace(args=("59",))
        intercepted = " ".join(c.command.chain)

    @manage.register("example")
    def example(x: str):
        nonlocal called
        assert True
        called = x

    manage.run("example", "hi world")
    assert "error" not in capsys.readouterr().out
    assert called == "59"
    assert intercepted == "example"

def test_before_hook_with_limited_commands(manage, capsys):
    called = False
    intercepted = ""

    @manage.before("example")
    def d(c: CommandContext):
        nonlocal intercepted
        c.replace(args=("59",))
        intercepted = " ".join(c.command.chain)

    @manage.register("example")
    def example(x: str):
        nonlocal called
        assert True
        called = x

    @manage.register("dont")
    def dont():
        pass

    manage.run("example", "hi world")
    manage.run("dont")
    assert "error" not in capsys.readouterr().out
    assert called == "59"
    assert intercepted == "example"

    

def test_after_hook(manage, capsys):
    called = False
    intercepted = ""
    success = False

    @manage.after()
    def d(c: CommandContext):
        nonlocal intercepted, success
        intercepted = " ".join(c.command.chain)
        success = c.success
        
    @manage.register("example")
    def example(x: str):
        nonlocal called
        assert True
        called = x

    manage.run("example", "59")
    assert "error" not in capsys.readouterr().out
    assert called == "59"
    assert intercepted == "example"
    assert success == True

def test_after_hook_limited(manage, capsys):
    called = False
    intercepted = ""
    success = False

    @manage.after("example")
    def d(c: CommandContext):
        nonlocal intercepted, success
        intercepted = " ".join(c.command.chain)
        success = c.success
        
    @manage.register("example")
    def example2(x: str):
        nonlocal called
        assert True
        called = x

    @manage.register("example4")
    def example(x: str):
        nonlocal called
        assert True
        called = x

    manage.run("example", "59")
    manage.run("example4", "59")
    assert "error" not in capsys.readouterr().out
    assert called == "59"
    assert intercepted == "example"
    assert success == True

def test_exception_catching(manage, capsys):
    called = False
    intercepted = ""
    success = False

    @manage.catch(TypeError)
    def d(c: TypeError):
        nonlocal intercepted, success
        success = isinstance(c, TypeError)
        

    @manage.register("example4")
    def example(x: str):
        nonlocal called
        raise TypeError
        called = True

    with pytest.raises(Exception):
        manage.run("example4", "59")
    assert called == False
    assert success == True


def test_exception_catching_with_mute(manage, capsys):
    called = False
    intercepted = ""
    success = False

    @manage.catch(TypeError)
    def d(c: TypeError):
        nonlocal intercepted, success
        success = isinstance(c, TypeError)
        return True
        

    @manage.register("example4")
    def example(x: str):
        nonlocal called
        raise TypeError
        called = True

    manage.run("example4", "59")
    assert called == False
    assert success == True

def test_exception_catching_with_mute_and_generic(manage, capsys):
    called = False
    intercepted = ""
    success = False

    @manage.catch(Exception)
    def d(c: Exception):
        nonlocal intercepted, success
        success = isinstance(c, TypeError)
        return True
        

    @manage.register("example4")
    def example(x: str):
        nonlocal called
        raise TypeError
        called = True

    manage.run("example4", "59")
    assert called == False
    assert success == True

