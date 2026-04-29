import sys
from io import StringIO
from contextlib import contextmanager

class Tee:
    def __init__(self, original, silent: bool = False):
        self.original = original
        self.buffer = StringIO()
        self._silent = silent

    def write(self, data):
        if not self._silent:
            self.original.write(data)
        self.buffer.write(data)
        return len(data)

    def flush(self):
        if not self._silent:
            self.original.flush()

    def getvalue(self):
        return self.buffer.getvalue()

@contextmanager
def tee_output(stdout_silent: bool = False, stderr_silent: bool = False):
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    stdout_tee = Tee(old_stdout, silent=stdout_silent)
    stderr_tee = Tee(old_stderr, silent=stderr_silent)

    try:
        sys.stdout = stdout_tee
        sys.stderr = stderr_tee
        yield stdout_tee, stderr_tee
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr