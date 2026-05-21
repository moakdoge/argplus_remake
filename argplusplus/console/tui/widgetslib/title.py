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
    def _selected(self):
        self._state = not self._state    
        
class Textbox(TUIStep):
    selectable = True
    def __init__(self, option: str, parent: "TUI", default: str = ""):
        self._str = option
        self._parent = parent
        self._text = default
    def render(self) -> str:
        return f"{self._str}: [{self._text}]"
    def _selected(self):
        try:
            for key in self._parent.console.raw:
                match key:
                    case '\x7f':
                        self._text = self._text[:-1]
                    case '\r':
                        break
                    case _:
                        self._text += key
                self._parent.draw()
        except KeyboardInterrupt as e:
            pass

class Choice(TUIStep):
    selectable = True
    def __init__(self, label: str, parent: "TUI", options: list[str], default: int = 0):
        self._str = label
        self._parent = parent
        self._options = options
        self._ind = default
    def render(self) -> str:
        return f"{self._str}: ({self._options[self._ind]})"
    def _selected(self):
        console = self._parent.console
        def _draw():
            console.clear()
            for i, opt in enumerate(self._options):
                frm = console.format(opt)
                if self._ind == i:
                    frm = console.format(f"[bold]{opt}[/bold]")
                console.print("\r" + frm)
        try:
            _draw()
            for key in self._parent.console.raw:
                match key:
                    case '\x7f':
                        break
                    case '\r':
                        break
                    case '\x1b[A': #up
                        self._ind -= 1
                        self._ind = max(0, self._ind)
                    case '\x1b[B': #down
                        self._ind += 1
                        self._ind = min(len(self._options), self._ind)
                    case _:
                        pass
                _draw()
                
        except KeyboardInterrupt as e:
            pass
