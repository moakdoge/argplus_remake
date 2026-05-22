from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable

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
        
class Button(TUIStep):
    selectable = True
    def __init__(self, option: str, parent: "TUI", callback: Callable[["TUI"], "None | bool | TUI"]):
        self._str = option
        self._parent = parent
        self._callback = callback
    def render(self) -> str:
        return f"({self._str})"
    
    def _selected(self):
        from argplusplus.console.tui.core import TUI
        child=TUI(self._parent.console)
        o = self._callback(child)
        if o is False:
            return
        if o is True:
            self._parent.exit()
            self._parent.console.clear()
            self._parent.console.raw.drain()
            return
        try:
            if isinstance(o, TUI):
                child.build()
        finally:
            self._parent.console.clear()
        self._parent.console.raw.drain()
        self._parent.draw()
        
class Textbox(TUIStep):
    selectable = True
    def __init__(self, option: str, parent: "TUI", default: str = ""):
        self._str = option
        self._parent = parent
        self._text = default
        self._cursor_pos = len(default)
        self._is_editing = False
    def render(self) -> str:
        # Only show cursor when actively editing
        if not self._is_editing:
            return f"{self._str}: [{self._text}]"
        
        before = self._text[:self._cursor_pos]
        after = self._text[self._cursor_pos:]
        cursor = "│"  # Vertical bar cursor
        return f"{self._str}: [{before}{cursor}{after}]"
    def _selected(self):
        self._is_editing = True
        start = self._text
        try:
            self._parent.draw()
            for key in self._parent.console.raw:
                if key.startswith("\x1b["):
                    match key:
                        case '\x1b[D':  # left arrow
                            self._cursor_pos = max(0, self._cursor_pos - 1)
                            self._parent.draw()
                        case '\x1b[C':  # right arrow
                            self._cursor_pos = min(len(self._text), self._cursor_pos + 1)
                            self._parent.draw()
                    continue
                match key:
                    case '\x7f':  # backspace
                        if self._cursor_pos > 0:
                            self._text = self._text[:self._cursor_pos - 1] + self._text[self._cursor_pos:]
                            self._cursor_pos -= 1
                    case '\r':
                        break
                    case '\x1b':
                        self._text = start
                        break
                    case _:
                        self._text = self._text[:self._cursor_pos] + key + self._text[self._cursor_pos:]
                        self._cursor_pos += 1
                self._parent.draw()
        except KeyboardInterrupt as e:
            pass
        finally:
            self._is_editing = False
class Password(TUIStep):
    selectable = True
    def __init__(self, option: str, parent: "TUI", symbol: str = "*"):
        self._str = option
        self._parent = parent
        self._text = ""
        self._sym = symbol
    def render(self) -> str:
        return f"{self._str}: [{self._sym * len(self._text)}]"
    def _selected(self):
        try:
            for key in self._parent.console.raw:
                if key.startswith("\x1b["):
                    continue
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
        orig = self._ind
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
                    case '\x1b': #esc
                        self._ind = orig
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


class Submenu(TUIStep):
    selectable = True

    def __init__(
        self,
        label: str,
        parent: "TUI",
        builder: Callable[["TUI"], "None | TUI"],
    ):
        self._str = label
        self._parent = parent
        self._builder = builder

    def render(self) -> str:
        return f"{self._str} >"


    @cached_property
    def child(self):
        from argplusplus.console.tui.core import TUI
        child=TUI(self._parent.console)
        o=self._builder(child)
        return child, o
    
    def _selected(self):
        from argplusplus.console.tui.core import TUI
        try:
        
            child, o = self.child
            child._running = True
            # Clear any buffered key so the child doesn't immediately exit.
            self._parent.console.raw.drain()
            if isinstance(o, TUI):
                child.build()
                
        finally:
            self._parent.console.clear()
            
        self._parent.console.raw.drain()
        self._parent.draw()