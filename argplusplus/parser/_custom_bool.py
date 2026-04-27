from functools import cached_property

TRUE_VALUES = ["y", "yes", "true", 1, "1"]
FALSE_VALUES = ["n", "no", "false", 0, "0"]

class BoolPlus:
    __slots__ = ("_raw")
    def __init__(self, value: str | bool) -> None:
        self._raw = value

    @property
    def _value(self):
        if self._raw in TRUE_VALUES:
            return True
        if self._raw in FALSE_VALUES:
            return False
        raise TypeError(f"{self._raw} is not a valid bool!")

    def __bool__(self):
        return self._value
        