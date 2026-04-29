from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class _Tag:
    raw: str
    name: str
    closing: bool
    start: int
    end: int
    content: str