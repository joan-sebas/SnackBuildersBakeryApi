from src.domain.value_objects.bake_time import BakeTime, Category
from src.domain.value_objects.ids import ItemId, MenuItemId, OrderId
from src.domain.value_objects.item_status import ItemStatus
from src.domain.value_objects.money import Money


class Item:
    """A single baked product within an order, progressing through the baking state machine."""

    def __init__(
        self,
        id: ItemId,
        order_id: OrderId,
        menu_item_id: MenuItemId,
        name: str,
        price: Money,
        category: Category,
        bake_time: BakeTime,
    ) -> None:
        self.id = id
        self.order_id = order_id
        self.menu_item_id = menu_item_id
        self.name = name
        self.price = price
        self.category = category
        self.bake_time = bake_time
        self._status = ItemStatus.WAITING

    @property
    def status(self) -> ItemStatus:
        return self._status

    @property
    def is_done(self) -> bool:
        return self._status is ItemStatus.DONE

    def start_baking(self) -> None:
        self._status = self._status.transition_to(ItemStatus.BAKING)

    def finish_baking(self) -> None:
        self._status = self._status.transition_to(ItemStatus.DONE)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Item):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
