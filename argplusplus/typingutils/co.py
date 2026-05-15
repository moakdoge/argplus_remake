from inspect import _empty
from typing import Any, get_origin, get_args, Annotated, Literal, Union
from types import UnionType
from pathlib import Path
from enum import Enum

from numpy import isin

from argplusplus.parser._custom_bool import BoolPlus
from argplusplus.parser.exceptions import InvalidArgumentType

def coerce_auto(value: str):
    for t in (int, float, str):
        try:
            return t(value)
        except Exception:
            pass

    raise InvalidArgumentType(f"Value {value!r} cannot be automatically coerced")

def clean_tp(tp: Any):
    origin = get_origin(tp)
    args = get_args(tp)
    if origin is Annotated:
        base, *meta = args
        return clean_tp(base)
    
    if origin in (Union, UnionType):
        _values = []
        for option in args:
            try:
                _values.append(clean_tp( option))
            except Exception:
                pass
        return f'{" | ".join(_values)}'
    
    if origin in (list, tuple):
        return f"{origin.__name__}[{clean_tp(args[0])}]"
    
    if origin in (dict,):
        return f"{origin.__name__}[{clean_tp(args[0])}, {clean_tp(args[1])}]"

    if origin in (Literal,):
        l=[]
        for a in args:
            if isinstance(a, str):
                a = f"'{a}'"
            elif isinstance(a, float):
                a = f"{a:.3f}"
            a = str(a)
            l.append(a)
        return f"{origin.__name__}[{", ".join(l)}]"

    if hasattr(tp, "__name__"):
        return tp.__name__

def convert_value(value: str, tp: Any):
    origin = get_origin(tp)
    args = get_args(tp)
    

    if tp is Any or tp is _empty:
        return coerce_auto(value)

    if origin is Annotated:
        base, *meta = args
        converted = convert_value(value, base)
        for item in meta:
            if (
                isinstance(item, tuple)
                and len(item) == 3
                and item[0] == "rng"
            ):
                min_val, max_val = item[1], item[2]
                try:
                    if min_val is not None and converted < min_val:
                        raise InvalidArgumentType(
                            f"Value {converted!r} is below minimum {min_val!r}"
                        )
                    if max_val is not None and converted > max_val:
                        raise InvalidArgumentType(
                            f"Value {converted!r} is above maximum {max_val!r}"
                        )
                except TypeError as exc:
                    raise InvalidArgumentType(
                        f"Value {converted!r} cannot be compared to range bounds"
                    ) from exc
        return converted

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
            f"Value {value!r} cannot be coerced to {clean_tp(tp)}"
        )