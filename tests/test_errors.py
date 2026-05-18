from re import I

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argplusplus as argpp
from argplusplus.parser import exceptions
@pytest.fixture
def manage():
    return argpp.manager.CommandManager("test")


### REAL TESTS ###

def test_non_existant_command(manage, capsys):
    called = False
    @manage.register("example")
    def example():
        nonlocal called
        assert True
        called = True

    with pytest.raises(exceptions.InvalidCommmand):
        manage.run("not_real")
    assert called is False

def test_missing_param(manage, capsys):
    called = False
    @manage.register("example")
    def example(x: int):
        nonlocal called
        assert True
        called = True

    with pytest.raises(exceptions.MissingArgument):
        manage.run("example")
    assert called is False

def test_missing_required_kparam(manage, capsys):
    called = False
    @manage.register("example")
    def example(*, x: int):
        nonlocal called
        assert True
        called = True

    manage.run("example", "12")
    assert called is True


def test_negative_number_not_flag(manage, capsys):
    called = False

    @manage.register("example")
    def example(x: int):
        nonlocal called
        called = x

    manage.run("example", "-4")
    assert "error" not in capsys.readouterr().out
    assert called == -4


def test_negative_number_keyword_arg(manage, capsys):
    called = False

    @manage.register("example")
    def example(x: int):
        nonlocal called
        called = x

    manage.run("example", "--x=-4")
    assert "error" not in capsys.readouterr().out
    assert called == -4


def test_negative_number_mixed_args(manage, capsys):
    called = False

    @manage.register("example")
    def example(x: int, *, y: int):
        nonlocal called
        called = (x, y)

    manage.run("example", "-4", "--y=-8")
    assert "error" not in capsys.readouterr().out
    assert called == (-4, -8)
