import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argplusplus as argpp
from argplusplus.parser import exceptions
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


def test_bool_type_requires_value(manage):
    called = None

    @manage.register("example")
    def example(verbose: bool):
        nonlocal called
        called = verbose

    with pytest.raises(ValueError):
        manage.run("example", "--verbose")
    assert called is None


def test_bool_type_false_string_truthy(manage, capsys):
    called = None

    @manage.register("example")
    def example(verbose: bool):
        nonlocal called
        called = verbose

    manage.run("example", "--verbose=false")
    assert "error" not in capsys.readouterr().out
    assert called is True


def test_short_flags_cluster_sets_all(manage, capsys):
    called = None

    @manage.register("example")
    def example(x: Flag, y: Flag, z: Flag):
        nonlocal called
        called = (x, y, z)

    manage.run("example", "-xyz")
    assert "error" not in capsys.readouterr().out
    assert called == (True, True, True)


def test_short_flags_reject_non_flag_argument(manage):
    @manage.register("example")
    def example(x: Flag, y: int):
        pass

    with pytest.raises(exceptions.InvalidArgument):
        manage.run("example", "-xy")
