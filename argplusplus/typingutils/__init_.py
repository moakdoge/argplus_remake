from typing import Any, TypeAlias, Union


from typing import Any, TypeAlias, get_args, get_origin, Literal, Union
from types import UnionType
from collections.abc import Sequence

AnyType: TypeAlias = Any

def isinst(value: Any, tp: AnyType) -> bool:
    origin = get_origin(tp)
    args = get_args(tp)

    if tp is Any:
        return True

    if origin is Literal:
        return value in args

    if origin in (Union, UnionType):
        return any(isinst(value, arg) for arg in args)

    if origin is list:
        if not isinstance(value, list):
            return False

        inner = args[0] if args else Any
        return all(isinst(v, inner) for v in value)

    if origin is set:
        if not isinstance(value, set):
            return False

        inner = args[0] if args else Any
        return all(isinst(v, inner) for v in value)

    if origin is tuple:
        if not isinstance(value, tuple):
            return False

        if not args:
            return True

        # tuple[T, ...]
        if len(args) == 2 and args[1] is Ellipsis:
            return all(isinst(v, args[0]) for v in value)

        # tuple[A, B, C]
        if len(value) != len(args):
            return False

        return all(isinst(v, t) for v, t in zip(value, args))

    if origin is dict:
        if not isinstance(value, dict):
            return False

        key_t, val_t = args if args else (Any, Any)

        return all(
            isinst(k, key_t) and isinst(v, val_t)
            for k, v in value.items()
        )

    if origin is not None:
        # Handles list[str], dict[str, int], etc. fallback base check
        return isinstance(value, origin)

    return isinstance(value, tp)