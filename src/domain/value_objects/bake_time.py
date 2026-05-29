"""Fixed bake durations per product category."""

from dataclasses import dataclass
from enum import Enum


class Category(Enum):
    COOKIES = "cookies"
    PASTRIES = "pastries"
    BREADS = "breads"


_MINUTES_BY_CATEGORY: dict[Category, int] = {
    Category.COOKIES: 5,
    Category.PASTRIES: 10,
    Category.BREADS: 20,
}


@dataclass(frozen=True)
class BakeTime:
    minutes: int

    def __post_init__(self) -> None:
        if self.minutes <= 0:
            raise ValueError(f"BakeTime must be positive, got {self.minutes}")

    @classmethod
    def from_category(cls, category: Category) -> "BakeTime":
        return cls(minutes=_MINUTES_BY_CATEGORY[category])
