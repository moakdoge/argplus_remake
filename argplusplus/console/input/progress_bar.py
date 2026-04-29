import math
from typing import TYPE_CHECKING, Self


if TYPE_CHECKING:
    from . import console
class ProgressBar:
    def __init__(self, console: "console.OutputConsole", start: int = 0, end: int = 100, steps: int = 10, *, label: str = "") -> None:
        self.start = start
        self.end = end
        self.steps = steps
        self.complete: int= start
        self._console = console
        self._indent = self._console.size[1] - (self.steps + 8)
        self._label = label
        self._last_lines_made = 0

    def update(self, *, new: float | None = None, label: str | None = None):
        if new is not None and new >= 0:
            if new == 0:
                self.complete = self.start
            if new > 1:
                new = 1
            self.complete = math.floor(self.start + ((self.end - self.start)*new))
        if label is not None and isinstance(label, str):
            self._label = label
        self.render()
        

    def render(self):
        
        completed=self.complete
        remaining=self.end-self.complete
        hashes="■" * math.floor(completed / self.steps)
        spaces=" " * math.ceil(remaining / self.steps)
        per = (self.complete / self.end) if self.end > 0 and self.complete > 0 else 0
        space_count = (self._indent - len(self._label))
        self._console.replace_line(f"{self._label + " " if self._label.strip() != "" else ""}{" " * space_count}[{hashes}{spaces}] {(per*100):.0f}%", newline=False, bottom=True)
        self._last_lines_made = self._console._lines_made


    def __enter__(self) -> Self:
        self.update(new=0)
        self._console.hide_cursor()
        self.render()
        return self
    
    def __exit__(self, exc_type, exc, tb):
        self.update(new=1)
        self.render()
        self._console.show_cursor()
        self._console._sticky_line=None
        self._console.newline()
        return False