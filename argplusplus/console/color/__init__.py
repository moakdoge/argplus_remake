import re

from argplusplus.console.color._tag import _Tag

TAG_RE = re.compile(r"\[(/?)([a-zA-Z_][\w -]*|/)\]")
from ._color import _FormattingColor

COLORS = [
    # Standard
    _FormattingColor("black", "\033[30m", "\033[40m", "black"),
    _FormattingColor("red", "\033[31m", "\033[41m", "red"),
    _FormattingColor("green", "\033[32m", "\033[42m", "green"),
    _FormattingColor("yellow", "\033[33m", "\033[43m", "yellow"),
    _FormattingColor("blue", "\033[34m", "\033[44m", "blue"),
    _FormattingColor("magenta", "\033[35m", "\033[45m", "magenta"),
    _FormattingColor("cyan", "\033[36m", "\033[46m", "cyan"),
    _FormattingColor("white", "\033[37m", "\033[47m", "white"),

    # Bright
    _FormattingColor("bright_black", "\033[90m", "\033[100m", "bright_black"),
    _FormattingColor("bright_red", "\033[91m", "\033[101m", "bright_red"),
    _FormattingColor("bright_green", "\033[92m", "\033[102m", "bright_green"),
    _FormattingColor("bright_yellow", "\033[93m", "\033[103m", "bright_yellow"),
    _FormattingColor("bright_blue", "\033[94m", "\033[104m", "bright_blue"),
    _FormattingColor("bright_magenta", "\033[95m", "\033[105m", "bright_magenta"),
    _FormattingColor("bright_cyan", "\033[96m", "\033[106m", "bright_cyan"),
    _FormattingColor("bright_white", "\033[97m", "\033[107m", "bright_white"),
]


def _find_color(color_name:str, background: bool=False) -> _FormattingColor | None:
    color_name = color_name.strip(" ")
    for clr in COLORS:
        _name = clr.foreground_name if not background else clr.background_name
        if _name == color_name:
            return clr
    return None


def _find_tags(text: str) -> list[_Tag]:
    tags: list[_Tag] = []

    for match in TAG_RE.finditer(text):
        full = match.group(0)
        closing = bool(match.group(1))
        name = match.group(2)

        t = _Tag(full, name, closing or name == "/", match.start(), match.end(),
                 content=text[match.start():match.end()])
        tags.append(t)

    return tags

def _process_tags(st: str):
    tags = _find_tags(st)
    for tag in tags:
        print(tag.content, tag.start, tag.end)
        
