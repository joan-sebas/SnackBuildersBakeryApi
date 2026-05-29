from decimal import Decimal

from src.domain.entities.item import Item
from src.domain.exceptions import DomainError
from src.domain.value_objects.ids import CustomerId, OrderId
from src.domain.value_objects.money import Money
from src.domain.value_objects.order_status import OrderStatus
from src.domain.value_objects.priority import Priority


class Order:
    """An order placed by a customer, containing one or more items to be baked."""

    def __init__(
        self,
        id: OrderId,
        customer_id: CustomerId,
        priority: Priority,
        items: list[Item],
    ) -> None:
        if not items:
            raise DomainError("An order must contain at least one item")
        self.id = id
        self.customer_id = customer_id
        self.priority = priority
        self._items = list(items)
        self._status = OrderStatus.PENDING_PAYMENT

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def items(self) -> list[Item]:
        return list(self._items)

    @property
    def total_price(self) -> Money:
        total = Money(Decimal("0"))
        for item in self._items:
            total = total + item.price
        return total

    @property
    def all_items_done(self) -> bool:
        return all(item.is_done for item in self._items)

    def mark_paid(self) -> None:
        self._status = self._status.transition_to(OrderStatus.PAID)

    def mark_queued(self) -> None:
        self._status = self._status.transition_to(OrderStatus.QUEUED)

    def mark_baking(self) -> None:
        self._status = self._status.transition_to(OrderStatus.BAKING)

    def mark_ready(self) -> None:
        if not self.all_items_done:
            raise DomainError("Cannot mark order as ready while items are still baking")
        self._status = self._status.transition_to(OrderStatus.READY)

    def mark_delivered(self) -> None:
        self._status = self._status.transition_to(OrderStatus.DELIVERED)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
