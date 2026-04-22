from typing import Any


class Globals:
    def __init__(self) -> None:
        object.__setattr__(self, "_values", {})
    def __setattr__(self, name: str, value: Any) -> None:
        self._values[name] = value
    def __getattr__(self, name: str) -> Any:
        return self._values.get(name)
    def __getitem__(self, key):
        if key in self._values:
            return key
        raise AttributeError(f"Key {key} is not a valid global!")
    def __len__(self):
        return len(self._values)
    def __iter__(self):
        for k, v in self._values:
            yield k, v
    def __repr__(self) -> str:
        return "<Globals>"