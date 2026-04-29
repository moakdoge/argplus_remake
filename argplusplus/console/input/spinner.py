import threading
import time
from typing import TYPE_CHECKING, Self

from wkclp.types.widgets import SpinnerType


if TYPE_CHECKING:
    from . import console



_SPINNER_TYPES = {
    "ascii": ("<", "^", ">", "v"),

    "square": ("[■  ]", "[ ■ ]", "[  ■]", "[ ■ ]"),

    "classic": ("|", "/", "-", "\\"),

    "line": ("-", "=", "≡", "="),

    "dots": (".  ", ".. ", "...", " ..", "  .", "   "),

    "circle": ("◐", "◓", "◑", "◒"),

    "arc": ("◜", "◠", "◝", "◞", "◡", "◟"),

    "blocks": ("▌", "▀", "▐", "▄"),

    "bounce": ("▉  ", " ▉ ", "  ▉", " ▉ "),

    "grow": ("▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"),

    "arrows": ("←", "↖", "↑", "↗", "→", "↘", "↓", "↙"),

    "triangles": ("◢", "◣", "◤", "◥"),

    "diamonds": ("◆", "◇", "◆", "◇"),

    "pulse": ("█", "▓", "▒", "░", "▒", "▓"),

    "bars": ("[=   ]", "[==  ]", "[=== ]", "[ ===]", "[  ==]", "[   =]"),

}

#_SPINNER_CHAR = ("[■  ]", "[ ■ ]", "[  ■]", "[ ■ ]") #("▌", "▀", "▐", "▄")#("<", "^", ">", "v")#("⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈")#("◜", "◠", "◝", "◞", "◡", "◟")#("⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈")#("▌", "▀", "▐", "▄")#("⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈")#("▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂")#("⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈")
class Spinner:
    def __init__(self, cons: "console.OutputConsole", label: str = "", spinner_type: SpinnerType = "square") -> None:
        self._console = cons
        self._frame = 0
        self._label = label
        self._selected = _SPINNER_TYPES[spinner_type]
        self._indent = (self._console.size[1]) - max([len(z) for z in self._selected])
        self._ticks = 0
        self._spinner_type = spinner_type
        self._active = True
        self._update_lock = threading.Lock()


    def _threaded_render(self):
        while self._active:
            self.render()
            time.sleep(0.05)

    def render(self):
        with self._update_lock:
            self._ticks += 1


            sz = max(0, self._indent - len(self.label))

            if self._ticks % 6 == 0:
                self._frame = (self._frame + 1) % len(self._selected)

            frame = self._selected[self._frame]

            self._console.replace_line(
                f"{self.label}{' ' * sz}{frame}",
                bottom=True,
                newline=False
            )
    def __enter__(self) -> Self:
        threading.Thread(target=self._threaded_render, daemon=True).start()
        self._console.hide_cursor()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._active = False
        self._console._sticky_line=None
        self._console.newline()
        self._console.show_cursor()
        return False
    
    def update(self, *, label: str | None = None, _type: SpinnerType | None = None):
        with self._update_lock:
            if label is not None:
                self._label = label
            if _type is not None:
                self._selected = _SPINNER_TYPES[_type]
                self._indent = (self._console.size[1]) - max([len(z) for z in self._selected])
                self._frame = 0
        #self.render()

    @property
    def label(self):
        return self._label