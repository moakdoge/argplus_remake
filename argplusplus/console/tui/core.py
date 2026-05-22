from typing import TYPE_CHECKING, Callable, Self

from argplusplus import stringutils
from argplusplus.console.tui.tui_obj import TUIStep
from argplusplus.console.tui.widgetslib.title import Button, Checkbox, Choice, DebugPrint, Password, Submenu, Title, Textbox


if TYPE_CHECKING:
    from argplusplus.console.input import console
    
class TUI():
    def __init__(self, console: "console.OutputConsole") -> None:
        self.console: "console.OutputConsole" = console
        self.steps: list[TUIStep] = []
        self._line_counter = 0
        self.cursor = 0
        self._running = True
        
    @property
    def selectable(self) -> list[TUIStep]:
        return [s for s in self.steps if s.selectable]
    
    @property
    def selected(self) -> TUIStep:
        return self.selectable[self.cursor]
    
    def exit(self):
        self._running= False
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
        with self.console.raw:
            # Highlight the initially selected item
            if self.selectable:
                try:
                    self.selectable[0]._hover()
                except NotImplementedError:
                    pass
            
            while self._running:
                self.draw()

                key = self.console.raw.readkey()

                if key is False:
                    raise KeyboardInterrupt

                if key is None:
                    break
                self.handle_key(key)
                if not self._running:
                    break
            self.console.raw.drain()
    def handle_key(self, key):
        match key:
            case "\x1b":
                self._running = False

            case "\r":
                self.selected._selected()
                pass

            case "\x1b[A":
                self.last_item()

            case "\x1b[B":
                self.next_item()
                
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
    
    def button(self, label: str, *, callback: Callable[["TUI"], "None | bool | TUI"]):
        t = Button(label, self, callback)
        self.steps.append(t)
        return self
    
    def textbox(self, option: str, *, default: str = ""):
        t = Textbox(option, self, default)
        self.steps.append(t)
        return self
    
    def password(self, option: str, *, symbol="*"):
        t = Password(option, self, symbol)
        self.steps.append(t)
        return self
    
    def choice(self, label: str, options: list[str], *, default: int = 0):
        t = Choice(label=label, parent=self, options=options, default=default)
        self.steps.append(t)
        return self
    
    def submenu(self, label: str, menu: Callable[["TUI"], "None | TUI"]):
        t = Submenu(label, self, menu)
        self.steps.append(t)
        return self