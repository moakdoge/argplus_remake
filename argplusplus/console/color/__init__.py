import re

from argplusplus.console.color._tag import _RandomTag, _Tag

TAG_RE = re.compile(r"\[(/?)([^\]]+)\]")
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

    # Formatting (no background support)
    _FormattingColor("bold", "\033[1m", "", "bold", supports_background=False),
    _FormattingColor("dim", "\033[2m", "", "dim", supports_background=False),
    _FormattingColor("italic", "\033[3m", "", "italic", supports_background=False),
    _FormattingColor("underline", "\033[4m", "", "underline", supports_background=False),
    _FormattingColor("blink", "\033[5m", "", "blink", supports_background=False),
    _FormattingColor("reverse", "\033[7m", "", "reverse", supports_background=False),
    _FormattingColor("hidden", "\033[8m", "", "hidden", supports_background=False),
    _FormattingColor("strike", "\033[9m", "", "strike", supports_background=False),
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
        name = match.group(2).lower()
        bg = name.startswith("background") or name.startswith("bg")
        if bg:
            name = name.lstrip("background")
            name = name.lstrip("bg")
        name = name.strip(" ")


        if name.startswith("random:"):
            t = _RandomTag(full, name, closing or name == "/", match.start(), match.end(),
                 content=text[match.start():match.end()], background=bg).fix()
        else:
            t = _Tag(full, name, closing or name == "/", match.start(), match.end(),
                    content=text[match.start():match.end()], background=bg)
        tags.append(t)

    return tags

RESET = "\033[0m"

def _process_tags(st: str) -> str:
    tags = _find_tags(st)
    out: list[str] = []
    last = 0
    open_clrs: list[_FormattingColor] = []

    for tag in tags:
        out.append(st[last:tag.start])
        last = tag.end


        if hasattr(tag, "get"):
            out.append(tag.get())
            continue
        
        if tag.closing:
            c=_find_color(tag.name, background=tag.background)
            if c and (c.force_bg == tag.background):
                c.force_bg = False
                open_clrs.remove(c) # type: ignore
            else:
                raise Exception(f"Tag {tag.name} is not a valid closing tag!")
            out.append(RESET)
            #get all the existing tags
            for clr in open_clrs:
                out.append(clr.get())
            continue

        clr = _find_color(tag.name)
        if not clr:
            out.append(st[tag.start:tag.end])
            continue
        open_clrs.append(clr)
        clr.force_bg = tag.background
        out.append(clr.get())
    out.append(st[last:])

    return "".join(out)
