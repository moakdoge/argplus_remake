from dataclasses import dataclass
import os
from typing import TYPE_CHECKING, Any



if TYPE_CHECKING:
    from argplusplus.console.tui.core import TUI

class WidgetApp:
    base: "TUI"
    answer: Any = None
    def _bind(self, parent: "TUI"):
        self.base = parent
    def _build(self):
        raise NotImplementedError
        
@dataclass
class MessageBox(WidgetApp):
    title: str
    answer: bool = False
    key: str | None = None
    def _build(self):
        def assign(base: "TUI"):
            def _yes(t: "TUI"):
                self.answer = True
                return t.back(1)
            def _no(t: "TUI"):
                self.answer = False
                return t.back(1)
            base \
            .title(self.title) \
            .button("Yes", callback=_yes) \
            .button("No", callback=_no) \
            .build()
        assign(self.base)
        
@dataclass
class FileExplorer(WidgetApp):
    starting_path: str = "~"
    answer: str = ""
    def _build(self):
        self._current_path = os.path.expanduser(self.starting_path)
        self.layers = 0
        def assign(base: "TUI"):
            base.title(self._current_path)
            c=0
            
            files=os.listdir(self._current_path)
            files.insert(0, "..")
            for fi in files:
                if os.path.isfile(os.path.join(self._current_path, fi)):
                    continue
                def _on_dpress(b: "TUI", path: str = fi):
                    self._current_path = os.path.normpath(os.path.join(self._current_path, path))
                    self.base.steps.clear()
                    if path=="..":
                        self.layers -= 1
                    else:
                        self.layers += 1
                    assign(self.base)
                base.button(f"[ {fi} ]", callback=_on_dpress)
            for fi in files:
                if os.path.isdir(os.path.join(self._current_path, fi)):
                    continue
                def _on_press(b: "TUI", path: str = fi):
                    self.answer = os.path.normpath(os.path.join(self._current_path, path))
                    return b.back(self.layers + 1)
                base.button(f"{fi}", callback=_on_press)
            base.build()
        assign(self.base)