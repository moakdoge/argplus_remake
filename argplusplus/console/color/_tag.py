from dataclasses import dataclass
import random
import re
from typing import Any, Self
from urllib.parse import urlparse
import uuid




@dataclass(slots=True)
class _Tag:
    raw: str
    name: str
    closing: bool
    start: int
    end: int
    content: str
    background: bool 
    _format: bool = False
    @classmethod
    def valid(cls, input: str) -> bool:
        return True
    def get(self, closing: str | None = None) -> str | tuple[str, str]:
        '''DO NOT USE'''
        raise NotImplemented


@dataclass()
class _BaseTag(_Tag):
    command: str = ""
    _format: bool = False
    @classmethod
    def valid(cls, input: str) -> bool:
        if cls is _BaseTag:
            return False
        return input.startswith(cls.command)
    def __post_init__(self):
        self.name = self.name.removeprefix(self.command)
    def get(self, closing: str | None = None) -> str | tuple[str, str]:
        raise NotImplemented

@dataclass()
class _RandomTag(_BaseTag):
    command: str = "?random:"
    _random_digits: int = 0
    
    def __post_init__(self):
        self.name = self.name.replace(self.command, "")
        from argplusplus.console.color import process_tags
        self._random_digits = int(process_tags(self.name))
    
    def get(self, closing: str | None = None) -> str:
        dig = [str(random.randint(0, 9)) for i in range(self._random_digits)]
        return "".join(dig) # type: ignore
    
from datetime import datetime
@dataclass()
class _DateTag(_BaseTag):
    command: str = "?now"
    _format_type: str = ""
    
    @classmethod
    def valid(cls, input: str):
        if not input.startswith("?now"):
            return False
        try:
            v = datetime.now()
            l = v.strftime(input) 
        except Exception as e:
            return False
        return True
    
    def __post_init__(self):
        self._format_type = self.name.removeprefix("?now:")
    
    def get(self, closing: str | None = None) -> str:
        if self._format_type.strip(" ") == "":
            return f"{datetime.now().isoformat()}"
        return f"{datetime.now().strftime(self._format_type)}"
    


VARIABLES: dict[str, str] = {
}

@dataclass()
class _AssignVariable(_BaseTag):
    command = "$"
    _format_type: str = ""
    
    @classmethod
    def valid(cls, input: str):
        if input.startswith("$") and ":" in input:
            return True
        return False
    
    def __post_init__(self):
        e = self.name.removeprefix("$")
        name, _, value = e.partition(":")
        self._var_name = name
        self._var_value = value

    
    def get(self, closing: str | None = None) -> str:
        import argplusplus.console.color as clr
        global VARIABLES
        VARIABLES[self._var_name] = clr.process_tags(str(self._var_value))
        return ""
    
_existing_ifs: list["_If"] = []
@dataclass()
class _If(_BaseTag):
    command = "if"
    _format_type: str = ""
    
    @classmethod
    def valid(cls, input: str):
        if input.startswith("if"):
            return True
        return False
    
    def __post_init__(self):
        e = self.name.removeprefix("if")
        name, _, value = e.partition(":")
        # store the raw expression so it can be evaluated at closing time
        # (this allows variable changes inside the block to affect the condition)
        self._expr = value
        if not self.closing:
            _existing_ifs.append(self)
    def get(self, closing: str | None = None) -> tuple[str, str]:
        import argplusplus.console.color as clr
        if closing is None:
            return "", ""
        if len(_existing_ifs) < 1:
            return clr.process_tags(closing), ""
        ext = _existing_ifs.pop()
        # evaluate the stored expression now so the condition reflects current state
        cond = clr.process_tags(ext._expr).strip("\n")
        if len(cond) >= 1:
            proc = clr.process_tags(closing)
            return proc, ""
        return clr.process_tags(closing), ""
    

@dataclass()
class _While(_BaseTag):
    command = "while"
    _format_type: str = ""
    _tag_index: int | None = None
    _loop_index: int | None = None
    _loop_reset: int | None = None
    _should_loop: bool = False
    _while_expr: str | None = None
    
    @classmethod
    def valid(cls, input: str):
        if input.startswith("while"):
            return True
        return False
    
    def __post_init__(self):
        e = self.name.removeprefix("while")
        name, _, value = e.partition(":")
        # store the raw expression so it can be evaluated at closing time
        # (this allows variable changes inside the block to affect the condition)
        self._expr = value
        self._loop_index = None
    def get(self, closing: str | None = None) -> tuple[str, str]:
        import argplusplus.console.color as clr
        if closing is None:
            return "", ""
        if self._while_expr is None:
            raise Exception("while closing tag missing opening while expression")
        self._should_loop = False
        
        # evaluate the stored expression now so the condition reflects current state
        cond = clr.process_tags(self._while_expr).strip("\n")
        if len(cond) <= 0:
            proc = clr.process_tags(closing)
            return proc, ""
        self._should_loop = True
        return "", ""
    

@dataclass
class _Sub(_BaseTag):
    command = "@sub"
    def get(self, closing: str | None = None):
        import argplusplus.console.color as clr
        _, _, args = self.name.partition(":")
        left, right = clr.split_top_level(args, ":", maxsplit=1)

        l = clr.process_tags(left)
        r = clr.process_tags(right)

        try:
            return str(float(l) - float(r))
        except:
            try:
                s=int((len(l)-1)-float(r))
                return l[0:s]
            except Exception as e:
                return ""

               
@dataclass
class _Add(_BaseTag):
    command = "@add"
    def get(self, closing: str | None = None):
        import argplusplus.console.color as clr
        _, _, args = self.name.partition(":")
        left, right = clr.split_top_level(args, ":", maxsplit=1)

        l = clr.process_tags(left)
        r = clr.process_tags(right)

        try:
            return str(float(l) + float(r))
        except:
            return str(l)+str(r)

@dataclass
class _Variable(_BaseTag):
    command = "$"

    
    def __post_init__(self):
        self._name = self.name.removeprefix("$")
        
    
    def get(self, closing: str | None = None) -> str:
        if self._name in VARIABLES:
            return VARIABLES[self._name]
        return ""
@dataclass
class _Gt(_BaseTag):
    command: str = "@gt"
    def get(self, closing : None | str = None) -> str:
        import argplusplus.console.color as clr 
        x=clr.split_top_level(self.name, ":", maxsplit=2)[1:]
        val1 = clr.process_tags(x[0])
        val2 = float(clr.process_tags(x[1]))
        try:
            val1=float(val1)
        except Exception as e:
            val1=len(val1)
        
        if val1 > val2:
            return "1"
        return ""

@dataclass
class _Eq(_BaseTag):
    command: str = "@eq"
    def get(self, closing : None | str = None) -> str:
        import argplusplus.console.color as clr 
        x=clr.split_top_level(self.name, ":", maxsplit=2)[1:]
        val1 = clr.process_tags(x[0])
        val2 = clr.process_tags(x[1])        
        if val1 == val2:
            return "1"
        return ""
    

@dataclass
class _Not(_BaseTag):
    command: str = "@not"
    def get(self, closing : None | str = None) -> str:
        import argplusplus.console.color as clr 
        x=clr.split_top_level(self.name, ":", maxsplit=1)[1:]
        val1 = clr.process_tags(x[0])
        
        if len(val1) == 0:
            return "1"
        return ""
@dataclass
class _Lt(_BaseTag):
    command: str = "@lt"
    def get(self, closing : None | str = None) -> str:
        import argplusplus.console.color as clr 
        x=clr.split_top_level(self.name, ":", maxsplit=2)[1:]
        val1 = clr.process_tags(x[0])
        val2 = float(clr.process_tags(x[1]))
        try:
            val1=float(val1)
        except Exception as e:
            val1=len(val1)

        if val1 < val2:
            return "1"
        return ""
    
@dataclass
class _jmp(_BaseTag):
    command: str = "!jmp"
    def get(self, closing : None | str = None) -> str:
        import argplusplus.console.color as clr 
        x=clr.split_top_level(self.name, ":", maxsplit=1)[1:]
        val2 = int(x[0])
        return val2 # type: ignore
@dataclass
class _Len(_BaseTag):
    command = "@len"
    def __post_init__(self):
        self._name = self.name.removeprefix("@")
        name, _, val = self._name.partition(":")
        self._expr = val
    def get(self, closing: str | None = None) -> str:
        import argplusplus.console.color as clr
        return str(len(clr.process_tags(self._expr)))


class _Subin():
    def __init__(self, val: str):
        self.value = val


@dataclass
class _Upper(_BaseTag):
    command = "upper"
    def get(self, closing: str | None = None) -> tuple[str, str]:
        if closing is None:
            return "", ""
        return ("", closing.upper()) # type: ignore
    
@dataclass
class _UUID4(_BaseTag):
    command = "uuid"
    def get(self, closing: str | None = None) -> tuple[str, str]:
        return (str(uuid.uuid4()), "") # type: ignore
@dataclass
class _Lower(_BaseTag):
    command = "lower"
    def get(self, closing: str | None = None) -> tuple[str, str]:
        if closing is None:
            return "", ""
        return ("", closing.lower()) # type: ignore
    
URL_REGEX = re.compile(
    r'^(https?:\/\/)'          # scheme
    r'(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})'  # domain
    r'(:\d+)?'                 # optional port
    r'(\/[^\s]*)?$'            # path
)
@dataclass
class _Url(_BaseTag):
    command: str = "link"
    _format: bool = True
    @classmethod
    def valid(cls, input: str) -> bool:
        return super().valid(input)

    def get(self, closing: str | None = None) -> tuple[str, str]:
        if closing:
            return "", f"[underline][blue]\033]8;;{closing}\033\\{closing}\033]8;;\033\\\0[/blue][/underline]"
        return "", ""

@dataclass
class _Literal(_BaseTag):
    command: str = "literal"
    @classmethod
    def valid(cls, input: str) -> bool:
        return super().valid(input)

    def get(self, closing: str | None = None) -> str:
        # Return the closing text with double brackets converted to single
        if closing:
            # Replace [[ with [ and ]] with ]
            return closing.replace("[[", "[").replace("]]", "]")
        return ""

TAG_TYPES: list[type[_BaseTag]] = _BaseTag.__subclasses__()
TAG_TYPES.append(_Tag) # type: ignore
