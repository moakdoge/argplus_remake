
from functools import cached_property
from typing import TYPE_CHECKING, Callable, Any
from argplusplus import stringutils
from argplusplus.console.tui.tui_obj import TUIStep
if TYPE_CHECKING:
    from argplusplus.console.tui.core import TUI

        
class Textbox(TUIStep):
    selectable = True
    def __init__(self, label: str, default: str = "", placeholder: str = "Type things here...", key: str | None = None):
        self._str = label
        self._text = default
        self._cursor_pos = len(default)
        self._is_editing = False
        self._placeholder = placeholder
        self.key = key
    def value(self) -> Any:
        return self._text
    def render(self) -> str:
        # Only show cursor when actively editing
        if not self._is_editing:
            if stringutils.is_blank(self._text):
                f=self.parent.console.format(f"[gray]{self._placeholder}[/gray]")
                return f"{self._str}:  [{f}]"
            return f"{self._str}: {{{self._text}}}"
        
        before = self._text[:self._cursor_pos]
        after = self._text[self._cursor_pos:]
        cursor = "│"  # Vertical bar cursor
        return f"{self._str}: [{before}{cursor}{after}]"
    def _selected(self):
        self._is_editing = True
        start = self._text
        try:
            self.parent.draw()
            for key in self.parent.console.raw:
                if key.startswith("\x1b["):
                    match key:
                        case '\x1b[D':  # left arrow
                            self._cursor_pos = max(0, self._cursor_pos - 1)
                            self.parent.draw()
                        case '\x1b[C':  # right arrow
                            self._cursor_pos = min(len(self._text), self._cursor_pos + 1)
                            self.parent.draw()
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
                self.parent.draw()
        except KeyboardInterrupt as e:
            pass
        finally:
            self._is_editing = False
class Password(TUIStep):
    selectable = True
    def __init__(self, label: str, symbol: str = "*", placeholder: str = "Password here...", key: str | None = None):
        self._str = label
        self._text = ""
        self._sym = symbol
        self._placeholder = placeholder
        self.key = key
    def value(self) -> Any:
        return self._text
    def render(self) -> str:
        if stringutils.is_blank(self._text):
            f=self.parent.console.format(f"[gray]{self._placeholder}[/gray]")
            return f"{self._str}:  [{f}]"
        return f"{self._str}: [{self._sym * len(self._text)}]"
    
    def _selected(self):
        try:
            for key in self.parent.console.raw:
                if key.startswith("\x1b["):
                    continue
                match key:
                    case '\x7f':
                        self._text = self._text[:-1]
                    case '\r':
                        break
                    case _:
                        self._text += key
                self.parent.draw()
        except KeyboardInterrupt as e:
            pass