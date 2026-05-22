from functools import cached_property
from typing import TYPE_CHECKING, Callable, Any
from argplusplus import stringutils
from argplusplus.console.tui.tui_obj import TUIStep
if TYPE_CHECKING:
    from argplusplus.console.tui.core import TUI

        
class Checkbox(TUIStep):
    selectable = True
    def __init__(self, label: str, state: bool = False, key: str | None = None):
        self._str = label
        self._state = state
        self.key = key
    def render(self) -> str:
        return f"{self._str}: {"([green]●[/green])" if self._state else "([red]●[/red])"}"
    def _selected(self):
        self._state = not self._state
    def value(self) -> Any:
        return self._state    
        

class Choice(TUIStep):
    selectable = True
    def __init__(self, label: str, options: list[str], default: int = 0, key: str | None = None):
        self._str = label
        self._options = options
        self._ind = default
        self.key = key
    def value(self) -> Any:
        return self._options[self._ind]
    def render(self) -> str:
        return f"{self._str}: ({self._options[self._ind]})"
    def _selected(self):
        from argplusplus.console.tui.core import TUI
        UI = TUI(self.parent.console)
        UI.title(self._str)
        _t = None
        for i, opt in enumerate(self._options):
            def fn(t, i=i):
                self._ind = i
                return True
            UI.button(label=opt, callback=fn)
            if i == self._ind:
                _t = UI.selectable[-1]
        if _t:
            UI.selected = _t
        UI.build()

