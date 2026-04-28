from functools import cached_property

TRUE_VALUES = ["y", "yes", "true", 1, "1", True]
FALSE_VALUES = ["n", "no", "false", 0, "0", False]

class BoolPlus:
    @staticmethod
    def check(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            val = val.lower()
        if val in TRUE_VALUES:
            return True
        if val in FALSE_VALUES:
            return False
        raise TypeError(f"{val} is not a valid bool!")
