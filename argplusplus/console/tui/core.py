from typing import TYPE_CHECKING, Callable, Self

from argplusplus import stringutils
from argplusplus.console.tui.tui_obj import TUIStep



if TYPE_CHECKING:
    from argplusplus.console.input import console
    
class TUI():
    def __init__(self, console: "console.OutputConsole") -> None:
        self.console: "console.OutputConsole" = console
        self.steps: list[TUIStep] = []
        self._line_counter = 0
        self.cursor = 0
        self._running = True
        self.parent: "None | TUIStep" = None
        
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
        self.console.hide_cursor()
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
        for _ in self.steps:
            _._bind(self)
        with self.console.raw:
            # Highlight the initially selected item (only if user hasn't set it manually)
            if self.selectable and self.cursor == 0:
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
        self.console.show_cursor()
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
                
    def back(self, amount: int = 1):
        return amount 
    
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
    
    def get_values(self) -> dict:
        """Get all values from widgets with keys set"""
        values = {}
        for step in self.steps:
            if hasattr(step, 'key') and step.key is not None:
                if hasattr(step, 'value'):
                    if stringutils.is_blank(step.key):
                        continue
                    values[step.key] = step.value()
        return values
        
    
        
    def title(self, label: str) -> Self:
        from argplusplus.console.tui.widgetslib.text import Title
        t = Title(label)
        self.steps.append(t)
        return self
    
    def paragraph(self, content: str) -> Self:
        from argplusplus.console.tui.widgetslib.text import Paragraph
        t = Paragraph(content)
        self.steps.append(t)
        return self
    
    def checkbox(self, label: str, *, checked: bool = False, key: str | None = None):
        from argplusplus.console.tui.widgetslib.other import Checkbox
        t = Checkbox(label=label, state=checked, key=key)
        self.steps.append(t)
        return self
    
    def button(self, label: str, callback: Callable[["TUI"], "None | bool | int | TUI"], * , key: str | None = None):
        from argplusplus.console.tui.widgetslib.nesting import Button
        t = Button(label, callback, key=key)
        self.steps.append(t)
        return self
    
    def textbox(self, label: str, *, default: str = "", key: str | None = None):
        from argplusplus.console.tui.widgetslib.input import Textbox
        t = Textbox(label, default=default, key=key)
        self.steps.append(t)
        return self
    
    def password(self, label: str, *, symbol="*", key: str | None = None):
        from argplusplus.console.tui.widgetslib.input import Password
        t = Password(label, symbol=symbol, key=key)
        self.steps.append(t)
        return self
    
    def choice(self, label: str, options: list[str], *, default: int = 0, key: str | None = None):
        from argplusplus.console.tui.widgetslib.other import Choice
        t = Choice(label=label, options=options, default=default, key=key)
        self.steps.append(t)
        return self
    
    def submenu(self, label: str, menu: Callable[["TUI"], "None | TUI"], key: str | None = None):
        from argplusplus.console.tui.widgetslib.nesting import Submenu
        t = Submenu(label, menu, key=key)
        self.steps.append(t)
        return self
    
    def spacer(self):
        from argplusplus.console.tui.widgetslib.text import Spacer
        t = Spacer()
        self.steps.append(t)
        return self
    
    