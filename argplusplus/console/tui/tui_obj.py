from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from argplusplus.console.tui.core import TUI

class TUIStep():
    _parent: "TUI"
    def render(self) -> str:
        raise NotImplementedError