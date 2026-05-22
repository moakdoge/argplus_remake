from functools import cached_property
from typing import TYPE_CHECKING, Callable, Any, Literal, Optional
from argplusplus import stringutils
from argplusplus.console.input.keyinp import ENTER, ESCAPE, LEFT, RIGHT, UP
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

class Slider(TUIStep):
    selectable = True
    def __init__(self, 
                 label: str, 
                 min: int = 0, 
                 max: int = 100, 
                 default: int = 50, 
                 step: int = 5, 
                 key: Optional[str] = None,
                 transform: Literal["percent", "count", "steps"] | None | str  | Callable[[int], None] = "percent"
                 ):
        self.key = key
        self._label = label
        self._min = min
        self._max = max
        self._value = default
        self._step = step
        self._transform = transform
        

    def _get(self):
        if callable(self._transform):
            return self._transform(self._value)
        
        if self._transform is None:
            self._transform = "percent"
            return self._get()

        match self._transform:
            case "percent":
                return f"{(self._value / self._max)*100:.0f}%"
            case "count":
                return self._value
            case "steps":
                return self._value // self._step
            case _:
                return f"{self._value // self._step}{self._transform}"
            
    def render(self) -> str:
        hash_count = self._value
        space_count = self._max - hash_count
        return f"{self._label}: [{"█" * (hash_count//self._step)}{"░"*(space_count//self._step)}] {self._get()}"
    def _selected(self):
        start = self._value
        with self.parent.console.raw:
            for key in self.parent.console.raw:
                if key == ENTER:
                    break
                if key == ESCAPE:
                    self._value = start
                    break
                if key == RIGHT:
                    self._value += self._step
                if key == LEFT:
                    self._value -= self._step
                
                self._value = max(self._min, self._value)
                self._value = min(self._max, self._value)
                self.parent.draw()
                        
    def value(self) -> Any:
        return self._value