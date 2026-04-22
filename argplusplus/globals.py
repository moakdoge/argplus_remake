from typing import Any


class Globals:
    def __init__(self) -> None:
        object.__setattr__(self, "_values", {})
    def __setattr__(self, name: str, value: Any) -> None:
        self._values[name] = value
    def __getattr__(self, name: str) -> Any:
        return self._values.get(name)