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

    def readkey(self) -> str | None:
        import select, os
        tm = 0.02 #time between esc 

        def _read_char(fd: int, timeout: float | None = None) -> str | None:
            if timeout is not None:
                ready, _, _ = select.select([fd], [], [], timeout)
                if not ready:
                    return None

            data = os.read(fd, 1)
            return data.decode(errors="ignore") if data else None

        if not self.stdin.isatty():
            ch = self.stdin.read(1)
            return ch if ch else None

        fd = self.stdin.fileno()
        key = _read_char(fd)

        if key == "\x03": #CTRL + C
            return None

        if key != "\x1b":
            if key == "\n":
                return "\r"
            if key == "\r":
                # Swallow a trailing LF if the terminal sends CRLF.
                _read_char(fd, 0)
            return key

        next_char = _read_char(fd, tm)
        if next_char is None:
            return "\x1b"

        seq = "\x1b" + next_char

        if next_char == "[":
            while True:
                char = _read_char(fd, tm)
                if char is None:
                    break

                seq += char

                if "@" <= char <= "~":
                    break

        return seq

    def drain(self) -> None:
        pass

    def __iter__(self):
        while True:
            key = self.readkey()

            if key is False or key is None:
                raise KeyboardInterrupt
            
            
            yield key