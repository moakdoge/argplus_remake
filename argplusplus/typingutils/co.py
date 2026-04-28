from inspect import _empty
from typing import Any, get_origin, get_args, Annotated, Literal, Union
from types import UnionType
from pathlib import Path
from enum import Enum

from argplusplus.parser._custom_bool import BoolPlus
from argplusplus.parser.exceptions import InvalidArgumentType
def coerce_auto(value: str):
    for t in (int, float, str):
        try:
            return t(value)
        except Exception:
            pass

    raise InvalidArgumentType(f"Value {value!r} cannot be automatically coerced")

def convert_value(value: str, tp: Any):
    origin = get_origin(tp)
    args = get_args(tp)

    if tp is Any or tp is _empty:
        return coerce_auto(value)

    if origin is Annotated:
        base, *_meta = args
        return convert_value(value, base)

    if origin is Literal:
        for lit in args:
            try:
                converted = convert_value(value, type(lit))
                if converted == lit:
                    return lit
            except Exception:
                pass
        raise InvalidArgumentType(f"Expected one of {args!r}, got {value!r}")

    if origin in (Union, UnionType):
        for option in args:
            try:
                return convert_value(value, option)
            except Exception:
                pass
        raise InvalidArgumentType(f"{value!r} does not match {tp!r}")

    if origin is list:
        inner = args[0] if args else str
        return [convert_value(part.strip(), inner) for part in value.split(",")]

    if origin is tuple:
        parts = [p.strip() for p in value.split(",")]

        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(convert_value(p, args[0]) for p in parts)

        if len(parts) != len(args):
            raise InvalidArgumentType(f"Expected {len(args)} values, got {len(parts)}")

        return tuple(convert_value(p, t) for p, t in zip(parts, args))

    if origin is dict:
        key_t, val_t = args if args else (str, str)
        out = {}

        if not value:
            return out

        for item in value.split(","):
            k, sep, v = item.partition("=")
            if not sep:
                raise InvalidArgumentType(f"Expected key=value, got {item!r}")

            out[convert_value(k.strip(), key_t)] = convert_value(v.strip(), val_t)

        return out

    if tp is bool:
        return bool(value)

    if isinstance(tp, type) and issubclass(tp, Enum):
        try:
            return tp[value]
        except KeyError:
            pass

        for member in tp:
            if str(member.value) == value:
                return member

        raise InvalidArgumentType(f"Invalid enum value {value!r}")

    try:
        return tp(value)
    except Exception:
        raise InvalidArgumentType(
            f"Value {value!r} cannot be coerced to {tp!r}"
        )