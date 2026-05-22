from functools import cached_property
from typing import TYPE_CHECKING, Callable
from argplusplus.console.tui.tui_obj import TUIStep
if TYPE_CHECKING:
    from argplusplus.console.tui.core import TUI


class Submenu(TUIStep):
    selectable = True

    def __init__(
        self,
        label: str,
        builder: Callable[["TUI"], "None | TUI"],
        key: str | None = None,
    ):
        self._str = label
        self._builder = builder
        self.key = key

    def render(self) -> str:
        return f"{self._str} ▶"


    @cached_property
    def child(self):
        from argplusplus.console.tui.core import TUI
        child=TUI(self.parent.console)
        child.parent = self.parent  # type: ignore
        o=self._builder(child)
        return child, o
    
    def _selected(self):
        from argplusplus.console.tui.core import TUI
        try:
        
            child, o = self.child
            child._running = True
            # Clear any buffered key so the child doesn't immediately exit.
            self.parent.console.raw.drain()
            if isinstance(o, TUI):
                child.build()
                
        finally:
            self.parent.console.clear()
            
        self.parent.console.raw.drain()
        self.parent.draw()
        
    def value(self):
        child, o = self.child
        return child.get_values()
    
class Button(TUIStep):
    selectable = True
    def __init__(self, label: str, callback: Callable[["TUI"], "None | int | bool | TUI"], key: str | None = None):
        self._str = label
        self._callback = callback
        self.key = key
    def render(self) -> str:
        return f"({self._str})"
    
    def _selected(self):
        from argplusplus.console.tui.core import TUI
        child=TUI(self.parent.console)
        child.parent = self.parent  # type: ignore
        o = self._callback(child)
        if o is False:
            return
        if o is True:
            self.parent.exit()
            self.parent.console.clear()
            self.parent.console.raw.drain()
            return
        
        if isinstance(o, int):
            # Exit n levels based on int return value
            levels = o
            current = self.parent
            while levels > 0 and current:
                current.exit()
                current = current.parent
                levels -= 1
            self.parent.console.clear()
            self.parent.console.raw.drain()
            return
        
        try:
            if isinstance(o, TUI):
                child.build()
        finally:
            self.parent.console.clear()
        self.parent.console.raw.drain()
        self.parent.draw()