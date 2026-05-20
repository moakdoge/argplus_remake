import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argplusplus as argpp


@pytest.fixture
def manage():
    return argpp.manager.CommandManager("test")


def test_root_command_runs_without_args(manage, capsys):
    called = False

    @manage.root()
    def root():
        nonlocal called
        called = True

    manage.run()
    assert "error" not in capsys.readouterr().out
    assert called is True


def test_help_on_root_command_lists_top_level(manage, capsys):
    @manage.root()
    def root():
        pass

    @manage.register("example")
    def example():
        pass

    manage.run("--help")
    assert "error" not in capsys.readouterr().out


def test_help_on_group_command_lists_children(manage, capsys):
    group = manage.group("parent")

    @group.register("child")
    def child():
        pass

    manage.run("parent", "--help")
    assert "error" not in capsys.readouterr().out


def test_help_on_subcommand_shows_options(manage, capsys):
    group = manage.group("parent")

    @group.register("child")
    def child(count: int):
        pass

    manage.run("parent", "child", "--help")
    assert "error" not in capsys.readouterr().out
