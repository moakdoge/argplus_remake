import sys

from .command import Command
import argparse
from functools import wraps
from typing import TypeVar, ParamSpec, Callable
P = ParamSpec('P')
R = TypeVar('R')

class CommandManager:
    def __init__(self, name: str, description: str = "N/A") -> None:
        self._main_parser = argparse.ArgumentParser(description=description)
        self.name = name
        self._command_tree = {}
        pass

    def _gen(self, dc, chain):
        current = dc

        for arg in chain:
            node = current.setdefault(arg, {
                "parser": None,
                "children": {}
            })
            current = node["children"]

        return node
            
            
    def _attach(self, subparsers, name, node):
        parser = subparsers.add_parser(name)
        node["parser"] = parser

        if node["children"]:
            child_sub = parser.add_subparsers(required=True)
            for child_name, child_node in node["children"].items():
                self._attach(child_sub, child_name, child_node)

    def _build(self):
        self._main_parser = argparse.ArgumentParser()
        sub = self._main_parser.add_subparsers(required=True)

        for name, node in self._command_tree.items():
            self._attach(sub, name, node)


    def register(self, *commands: str, author: str="") -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            
            #start making a tree
            last = self._command_tree
            self._gen(self._command_tree, list(commands))
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def process(self, args: list[str] | None = None):
        if args is None:
            args = sys.argv

        parsed = self._main_parser.parse_args(args)
        print(parsed)