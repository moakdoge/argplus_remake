from typing import TYPE_CHECKING, Any

from argplusplus.console.tui.tui_obj import TUIStep

if TYPE_CHECKING:
    from argplusplus.console.tui.core import TUI

class Title(TUIStep):
    def __init__(self, text: str, parent: "TUI"):
        self._str = text
        self._parent = parent
    def render(self) -> str:
        return f"[bold]{self._str}[/bold]"
    
class DebugPrint(TUIStep):
    def __init__(self, text: str, parent: "TUI"):
        self._str = text
        self._parent = parent
    def render(self) -> str:
        return f"CURSOR: {self._parent.cursor} [bold]{self._str}[/bold]"
    
class Checkbox(TUIStep):
    selectable = True
    def __init__(self, option: str, parent: "TUI", state: bool = False):
        self._str = option
        self._parent = parent
        self._state = state
    def render(self) -> str:
        return f"{self._str}: {"([green]x[/green])" if self._state else "[red]()[/red]"}"
    
