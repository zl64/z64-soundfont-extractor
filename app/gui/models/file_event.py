# currently unused

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class FileEventType(Enum):
    WRITE = 'write'
    SKIP = 'skip'
    REPLACE = 'replace'
    ERROR = 'error'


@dataclass
class FileEvent:
    type: FileEventType
    path: Path
    message: str | None = None