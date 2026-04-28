from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import sys


@dataclass(slots=True, frozen=True)
class ProcessContext:
    executable: Path
    pid: int

@dataclass(slots=True, frozen=True)
class ManagerContext:
    cwd: Path
    argv: list[str]
    start: datetime
    env: dict
    process: ProcessContext = ProcessContext(executable=Path(sys.executable), pid=os.getpid())
    @property
    def runtime(self):
        return datetime.now() - self.start