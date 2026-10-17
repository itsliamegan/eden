from dataclasses import dataclass
from typing import Literal

type Direction = Literal["asc", "desc"]


@dataclass
class Order:
	field: str
	direction: Direction
