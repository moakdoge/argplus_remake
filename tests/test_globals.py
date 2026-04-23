import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argplusplus as argpp
@pytest.fixture
def manage():
    return argpp.manager.CommandManager("test")


def test_basic_globals(manage):
    called = False
    @manage.register("example")
    def example():
        nonlocal called
        assert True
        called = manage.globals.examp

    manage.run("example")
    assert "error" not in capsys.readouterr().out
    assert called is True
