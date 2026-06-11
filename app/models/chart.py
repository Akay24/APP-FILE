from dataclasses import dataclass, field
from typing import List


@dataclass
class Series:
    name: str
    values: List[float] = field(default_factory=list)


@dataclass
class Chart:
    type: str = "chart"
    chart_id: str = ""
    chart_type: str = "bar"
    title: str = ""

    categories: List[str] = field(default_factory=list)
    series: List[Series] = field(default_factory=list)