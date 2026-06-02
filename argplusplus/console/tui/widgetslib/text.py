from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable, Optional

from argplusplus import stringutils
from argplusplus.console.tui.tui_obj import TUIStep

if TYPE_CHECKING:
    from argplusplus.console.tui.core import TUI

class Title(TUIStep):
    def __init__(self, text: str):
        self._str = text
    def render(self) -> str:
        return f"━━━━ {self._str} ━━━━"
    
class Paragraph(TUIStep):
    def __init__(self, text: str):
        self._str = text
    def render(self) -> str:
        import textwrap
        l = textwrap.wrap(self._str, width=100)
        l = ["||  " + _ for _ in l]
        return "\r\n".join(l)
          
class Spacer(TUIStep):
    def render(self) -> str:
        return "\n"
    
class Bar(TUIStep):
    def __init__(self, length: Optional[int] = None) -> None:
        self._length = length or 16
    def render(self) -> str:
        return "━"*self._length