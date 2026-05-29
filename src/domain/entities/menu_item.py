from src.domain.value_objects.bake_time import Category
from src.domain.value_objects.ids import MenuItemId
from src.domain.value_objects.money import Money


class MenuItem:
    """A product offered for sale, with a fixed price and bake category."""

    def __init__(
        self,
        id: MenuItemId,
        name: str,
        price: Money,
        category: Category,
        available: bool = True,
    ) -> None:
        self.id = id
        self.name = name
        self.price = price
        self.category = category
        self.available = available

    def enable(self) -> None:
        self.available = True

    def disable(self) -> None:
        self.available = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MenuItem):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
