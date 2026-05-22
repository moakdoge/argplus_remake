import re
import secrets

from argplusplus.console.color._tag import TAG_TYPES, VARIABLES, _RandomTag, _Subin, _Tag, _While, _jmp

TAG_RE = re.compile(r"\[(/?)((?:[^\[\]]|\[[^\[\]]*\])*)\]")
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

ESC = re.compile(r"(?<!\[)(\[{2,})(.*?)(\]{2,})(?!\])")
def iter_tag_spans(text: str):
    i = 0

    while i < len(text):
        if text[i] != "[":
            i += 1
            continue

        start = i
        i += 1
        depth = 1

        while i < len(text):
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1

                if depth == 0:
                    end = i + 1
                    yield start, end, text[start:end]
                    i = end
                    break

            i += 1
        else:
            # unmatched [
            break
def split_top_level(s: str, sep: str = ":", maxsplit: int = -1) -> list[str]:
    out: list[str] = []
    start = 0
    depth = 0
    splits = 0

    for i, ch in enumerate(s):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == sep and depth == 0 and (maxsplit < 0 or splits < maxsplit):
            out.append(s[start:i])
            start = i + 1
            splits += 1

    out.append(s[start:])
    return out
def _find_tags(text: str) -> list[_Tag]:
    tags: list[_Tag] = []

    for start, end, full in iter_tag_spans(text):
        inner = full[1:-1]
        
        # Skip ANSI escape sequences (incomplete tags like [4m, [24m, [4;24m, etc.)
        if '\x1b' in full or (inner and (inner[0].isdigit() or inner.split(';')[0].isdigit())):
            continue

        closing = inner.startswith("/")
        if closing:
            inner = inner[1:]

        name = inner.strip(" ")

        bg = name.startswith("background") or name.startswith("bg")
        if bg:
            if name.startswith("background"):
                name = name[len("background"):]
            elif name.startswith("bg"):
                name = name[len("bg"):]

        name = name.strip(" ")

        args = (
            full,
            name,
            closing or name == "/",
            start,
            end,
            full,
            bg,
        )

        for _t in TAG_TYPES:
            if _t.valid(name):
                tags.append(_t(*args))
                break

    return tags

RESET = "\033[0m"


def _find_last_visible_chunk(parts: list[str]) -> tuple[int | None, str]:
    for idx in range(len(parts) - 1, -1, -1):
        part = parts[idx]
        if not part:
            continue
        # Ignore ANSI control sequences when deciding what text to transform.
        visible = re.sub(r"\x1b\[[0-9;]*m", "", part)
        if visible:
            return idx, visible
    return None, ""

def process_tags(st: str) -> str:
    saved = []
    PLACEHOLER_LEFT=str(secrets.token_hex(6))
    PLACEHOLER_RIGHT=str(secrets.token_hex(6))
    def repl(m: re.Match[str]) -> str:
        left, inner, right = m.groups()
        saved.append(f"[{m.group(1)}]")
        return f"{PLACEHOLER_LEFT*(len(left)-1)}{inner}{PLACEHOLER_RIGHT*(len(right)-1)}"

    st = ESC.sub(repl, st)
    tags = _find_tags(st)
    out: list[str] = []
    last = 0
    open_clrs: list[_FormattingColor] = []
    while_stack: list[_While] = []
    i = 0
    while i < len(tags):
        tag = tags[i]
        #print(tag)
        if isinstance(tag, _jmp):
            i += int(tag.get())
            continue
        if isinstance(tag, _While) and not tag.closing:
            tag._tag_index = i
            while_stack.append(tag)
        out.append(st[last:tag.start])
        last = tag.end
        if tag.closing:
            if hasattr(tag, "get") and not tag.__class__ is _Tag:
                if isinstance(tag, _While):
                    if not while_stack:
                        raise Exception("while closing tag found without a matching opening tag")
                    opening = while_stack[-1]
                    tag._loop_index = opening._tag_index
                    tag._loop_reset = opening.end
                    tag._while_expr = opening._expr
                chunk_idx, closing_text = _find_last_visible_chunk(out)
                output = tag.get(closing=closing_text) # type: ignore
                if isinstance(output, tuple):
                    if isinstance(tag, _While) and getattr(tag, "_should_loop", False):
                        loop_index = getattr(tag, "_loop_index", None)
                        if loop_index is None:
                            raise Exception("while loop missing opening tag index")
                        i = loop_index
                        last = getattr(tag, "_loop_reset", last)
                        continue
                    if isinstance(tag, _While):
                        while_stack.pop()

                    if chunk_idx is not None:
                        out[chunk_idx] = output[1] if not tag._format else process_tags(output[1])
                    out.append(output[0])
                else:
                    out.append(output)
            else:
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
            i+=1
            continue
        if hasattr(tag, "get") and not tag.__class__ is _Tag:
            o=tag.get()
            if isinstance(o, tuple):
                o=o[0]
            if tag._format:
                o = process_tags(o)
            out.append(o) # type: ignore
            i+=1
            continue
        clr = _find_color(tag.name)
        if not clr:
            out.append(st[tag.start:tag.end])
            i+=1
            continue

        open_clrs.append(clr)
        clr.force_bg = tag.background
        out.append(clr.get())
        i+=1
    out.append(st[last:])
    return "".join(out).replace(PLACEHOLER_LEFT, "[").replace(PLACEHOLER_RIGHT, "]")
