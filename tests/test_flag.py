import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argplusplus as argpp
from argplusplus.types import Flag


@pytest.fixture
def manage():
    return argpp.manager.CommandManager("test")


def test_flag_type_defaults_false(manage, capsys):
    called = None

    @manage.register("example")
    def example(verbose: Flag):
        nonlocal called
        called = verbose

    manage.run("example")
    assert "error" not in capsys.readouterr().out
    assert called is False


def test_flag_type_true_when_passed(manage, capsys):
    called = None

    @manage.register("example")
    def example(verbose: Flag):
        nonlocal called
        called = verbose

    manage.run("example", "--verbose")
    assert "error" not in capsys.readouterr().out
    assert called is True


def test_flag_type_explicit_false_value(manage, capsys):
    called = None

    @manage.register("example")
    def example(verbose: Flag):
        nonlocal called
        called = verbose

    manage.run("example", "--verbose=false")
    assert "error" not in capsys.readouterr().out
    assert called is False
