from typing import TYPE_CHECKING, Any



if TYPE_CHECKING:
    from argplusplus.console.tui.core import TUI
    from argplusplus.console.input.console import OutputConsole

class TUIStep():
    selectable: bool = False
    _parent: "TUI"
    key = ""
    _bold: bool = False
    def __init__(self, parent: "TUI") -> None:
        self._parent = parent
        
    def render(self) -> str:
        raise NotImplementedError
    
    def _render(self) -> str:
        if self._bold:
            return f"> {self.render()}"
        return self.render()
    
    def _hover(self):
        '''Called when the object is hovered. Defaults to bolding.'''
        self._bold = True
    
    def _dehover(self):
        '''Called when the object is dehovered. Defaults to bolding.'''
        self._bold = False
        
    def _selected(self):
        '''Called when the object is selected'''
        pass
    
    def value(self) -> Any:
        '''The value of this;'''
        pass