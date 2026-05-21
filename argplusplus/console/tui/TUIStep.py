from typing import Any


class TUIStep:
    def render(self) -> str:
        raise NotImplementedError
    def value(self) -> Any:
        raise NotImplementedError