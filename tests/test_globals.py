import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argplusplus as argpp
@pytest.fixture
def manage():
    return argpp.manager.CommandManager("test")


def test_basic_globals(manage, capsys):
    called = False
    @manage.register("example")
    def example():
        nonlocal called
        assert True
        called = manage.globals.examp

    manage.define_global("examp", flag=True)
    manage.run("example", "--examp")
    assert "error" not in capsys.readouterr().out
    assert called is True

def test_basic_globals_values(manage, capsys):
    called = False
    @manage.register("example")
    def example():
        nonlocal called
        assert True
        called = manage.globals.examp

    manage.define_global("examp", _type=int)
    manage.run("example", "--examp=69")
    assert "error" not in capsys.readouterr().out
    assert called == 69

