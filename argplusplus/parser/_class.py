from functools import cached_property
import sys
from typing import Any


class Parser:
    def __init__(self, args: list[str] = sys.argv) -> None:
        self._raw_args = args
        self._keywords = []
        self._options = []
        for i, arg in enumerate(args[1:]):
            if arg.startswith("--"):
                self._options = args[1+i:]
                break
            self._keywords.append(arg)

        print(self._options, self._process_options(self._options))
        self._options_tuple: list[tuple[str, Any]] = []

    def _process_options(self, opt: list[str]) -> list[tuple[str, Any]]:
        pairs = []
        for i, _o in enumerate(opt):
            if _o.startswith("--") and not "=" in _o:
                if len(opt)-1 == i:
                    pairs.append((_o, True))
                    continue
                nxt = opt[i+1]
                if nxt.startswith("--"):
                    pairs.append((_o, True))
                    continue
                pairs.append((_o, opt[i+1]))
                continue
            elif _o.startswith("--") and "=" in _o:
                sp = _o.split("=")
                pairs.append((sp[0], sp[1]))
            
        return pairs
    
    @cached_property
    def caller(self):
        return self._raw_args[0]
    
    @cached_property
    def commands(self):
        return self._keywords