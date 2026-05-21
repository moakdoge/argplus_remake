from typing import TYPE_CHECKING, Self

from argplusplus import stringutils
from argplusplus.console.tui.tui_obj import TUIStep
from argplusplus.console.tui.widgetslib.title import Title


if TYPE_CHECKING:
    from argplusplus.console.input import console
    
class TUI():
    def __init__(self, console: "console.OutputConsole") -> None:
        self.console: "console.OutputConsole" = console
        self.steps: list[TUIStep] = []
        self._line_counter = 0
        
    def draw(self):
        self.console.move_cursor(lines=-self._line_counter)
        for step in self.steps:
            output = step.render()
            lc = stringutils.linecount(output)
            self._line_counter += (lc + 1)
            self.console.pprint("\r" + output)
        self.console.flush()
        
    def title(self, title: str) -> Self:
        t = Title(title,parent=self)
        self.steps.append(t)
        return self