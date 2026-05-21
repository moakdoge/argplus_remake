import math
import re
from typing import Literal
_NORMALIZE_ST = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]*$')

def is_blank(st: str) -> bool:
    '''Checks if a string is blank'''
    p1 = st.replace(" ", "")
    p2 = p1.strip("\n")
    return p2 == ""

def generate_dashes(st: str) -> str:
    '''Converts a string like `example string` or `example_string` to `example-string`'''
    return st.replace(" ", "-").replace("_", "-")

def normalize_name(st: str) -> str:
    '''Normallizes a function name to a good command; raises NameError if invalid.'''
    
    #first, let's clean it up
    new = generate_dashes(st)
    
    valid = _NORMALIZE_ST.fullmatch(new)
    if not valid:
        raise NameError(f"Function name of {st} is not valid!")
    
    return new

def get_padding(*strs: str) -> int:
    '''Gets the longest string, used for padding'''
    _max = max(len(s) for s in strs)
    x=math.ceil(_max)
    return x

def align_strs(*strs: str, alignment: Literal["left", "center", "right"] = "center", padding_size: int = 20):
    '''Returns a list of all strings aligned to a certain direction.'''
    padding = get_padding(*strs) * padding_size
    #print(padding)
    new_sts: list[str] = []
    match alignment:
        case "left":
            space_count = (" "*(padding*2))
            new_sts = [s + space_count for s in strs]
        case "center":
            space_count = (" " * padding)
            new_sts = [space_count + s + space_count for s in strs]
        case "right":
            space_count = (" "*(padding*2))
            new_sts = [space_count + s for s in strs]
        case _:
            raise TypeError(f"Alignment {alignment} not found; please choose left, center, or right!")
    return new_sts

def space_evenly(*strs: str, seperator_char: str = "") -> str:
    size = get_padding(*strs)
    if size <= 0:
        return seperator_char.join(strs)

    rendered: list[str] = []
    for s in strs:
        text = s
        if len(text) > size:
            if size <= 3:
                text = text[:size]
            else:
                text = text[: size - 3] + "..."

        padding = max(size - len(text), 0)
        left = padding // 2
        right = padding - left
        rendered.append((" " * left) + text + (" " * right))

    return seperator_char.join(rendered)

def bar(*strs: str, symbol: str = "|") -> list[str]:
    return [symbol + _ + symbol for _ in strs]

def linecount(st: str) -> int:
    '''Returns the amount of lines'''
    return st.count("\n")