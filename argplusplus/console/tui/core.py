from typing import TYPE_CHECKING, Callable, Self

from argplusplus import stringutils
from argplusplus.console.tui.tui_obj import TUIStep
from argplusplus.console.tui.widgetslib.title import Checkbox, Choice, DebugPrint, Submenu, Title, Textbox


if TYPE_CHECKING:
    from argplusplus.console.input import console
    
class TUI():
    def __init__(self, console: "console.OutputConsole") -> None:
        self.console: "console.OutputConsole" = console
        self.steps: list[TUIStep] = [DebugPrint("lmao", self)]
        self._line_counter = 0
        self.cursor = 0
        
    @property
    def selectable(self) -> list[TUIStep]:
        return [s for s in self.steps if s.selectable]
    
    @property
    def selected(self) -> TUIStep:
        return self.selectable[self.cursor]
    
    @selected.setter
    def selected(self, new: TUIStep):
        try:
            self.selected._dehover()
        except Exception as e:
            pass
        self.cursor = self.selectable.index(new)
        #print("NEW: ", self.cursor, new)
        try:
            new._hover()
        except NotImplementedError:
            pass
        
    def draw(self):
        if self.selectable and self.cursor >= len(self.selectable):
            self.cursor = 0
        self.console.clear()
        self.console.move_cursor(lines=-self._line_counter)
        self._line_counter = 0
        for step in self.steps:
            output = step._render()
            lc = stringutils.linecount(output)
            self._line_counter += (lc + 1)
            out=self.console.format(output)
            self.console.clear_line()
            self.console.raw_print("\r" + out + "\n", flush=False)
        self.console.flush()
        
    def build(self):
        self.draw()
        with self.console.raw:
            for key in self.console.raw:
                match key:
                    case '\x1b[A': #up
                        self.last_item()
                    case '\x1b[B': #down
                        self.next_item()
                    case '\x1b': #ESC
                        return
                    case '\r':
                        self.selected._selected()
                self.draw()
        
    def next_item(self):
        if not self.selectable:
            return
        current_ind = self.selectable.index(self.selected)
        if current_ind < len(self.selectable) - 1:
            self.selected = self.selectable[current_ind + 1]
        
    def last_item(self):
        if not self.selectable:
            return
        current_ind = self.selectable.index(self.selected)
        if current_ind > 0:
            self.selected = self.selectable[current_ind - 1]
        
    
        
    def title(self, title: str) -> Self:
        t = Title(title,parent=self)
        self.steps.append(t)
        return self
    
    def checkbox(self, option: str, *, state: bool = False):
        t = Checkbox(option, self, state=state)
        self.steps.append(t)
        return self
    
    def textbox(self, option: str, *, default: str = ""):
        t = Textbox(option, self, default)
        self.steps.append(t)
        return self
    
    def choice(self, label: str, options: list[str], *, default: int = 0):
        t = Choice(label=label, parent=self, options=options, default=default)
        self.steps.append(t)
        return self
    
    def submenu(self, label: str, menu: Callable[["TUI"], None]):
        t = Submenu(label, self, menu)
        self.steps.append(t)
        return self