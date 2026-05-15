from abc import ABC, abstractmethod
from typing import Annotated, Any, ClassVar, Generic, Self, get_type_hints, overload
from functools import wraps
from typing import TypeVar, ParamSpec, Callable
from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar("T")
X = TypeVar("X", bound=type)

class CustomType(Generic[R]):
    target_type: ClassVar[type[Any]] = str

    @classmethod
    def process(cls, argument: str) -> R | None:
        raise NotImplementedError

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.process,
            handler(cls.target_type),
        )


def custom_type(func: Callable[[str], R]) -> type[R]:
    hints = get_type_hints(func)
    return_type = hints.get("return", Any)

    class NewCls(CustomType[return_type]):  # type: ignore[valid-type]
        @classmethod
        def process(cls, argument: str):
            return func(argument)

    NewCls.__name__ = f"_{func.__name__}"
    NewCls.__module__ = func.__module__
    NewCls.__qualname__ = f"_{func.__qualname__}"
    NewCls.__doc__ = func.__doc__

    return NewCls # type: ignore

def custom_class(return_type: type[T]):
    def wrap(cls: type[CustomType]) -> type[T]:
        return cls  # type: ignore
    return wrap