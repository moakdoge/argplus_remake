from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable

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
    
class DebugPrint(TUIStep):
    def __init__(self, text: str):
        self._str = text
    def render(self) -> str:
        return f"CURSOR: {self.parent.cursor} [bold]{self._str}[/bold]"
    

        
class Spacer(TUIStep):
    def render(self) -> str:
        return "\n"