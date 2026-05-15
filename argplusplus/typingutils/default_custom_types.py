from typing import Annotated, Any, Generic, TypeVar

from .custom_type import T, CustomType, custom_class, custom_type



@custom_class(int)
class ExampleInt(CustomType[int]):
    @classmethod
    def process(cls, argument: str) -> int | None:
        return int(argument) * 2