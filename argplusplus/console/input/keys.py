import termios
import tty
from typing import TextIO


class KeyReader:
    def __init__(self, sysin: TextIO, sysout: TextIO) -> None:
        self.stdout = sysout
        self.stdin = sysin
        self.fd = None
        self.old = None

    def __enter__(self):
        self.fd = self.stdin.fileno()

        if self.stdin.isatty():
            self.old = termios.tcgetattr(self.fd)
            tty.setraw(self.fd)

        return self

    def __exit__(self, exc_type, exc, tb):
        if self.old is not None:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old) # type: ignore

        return False

    def readkey(self):
        if not self.stdin.isatty():
            ch = self.stdin.read(1)
            return ch if ch else None

        key = self.stdin.read(1)

        if key == "\x03":
            return False

        if key == "\x1b":
            seq = key
            next_char = self.stdin.read(1)

            if next_char:
                seq += next_char

                if next_char == "[":
                    while True:
                        char = self.stdin.read(1)
                        if not char:
                            break

                        seq += char

                        if "@" <= char <= "~":
                            break

            return seq

        return key

    def __iter__(self):
        while True:
            key = self.readkey()

            if key is False or key is None:
                break

            yield key