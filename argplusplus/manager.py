import sys

from .command import Command
import argparse
class CommandManager:
    def __init__(self, name: str, description: str = "N/A") -> None:
        self._main_parser = argparse.ArgumentParser(description=description)
        self.name = name
        pass

    def process(self, args: list[str] | None = None):
        if args is None:
            args = sys.argv

        parsed = self._main_parser.parse_args(args)
        print(parsed)