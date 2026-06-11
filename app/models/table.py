from dataclasses import dataclass, field
from typing import List


@dataclass
class Table:
    type: str = "table"
    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)