from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class ExceptionCatcher:
    function: Callable
    exception_type: tuple[type[Exception], ...] = ()