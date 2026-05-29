from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from src.domain.exceptions import InvalidStateTransitionError

if TYPE_CHECKING:
    pass


class OrderStatus(Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    QUEUED = "queued"
    BAKING = "baking"
    READY = "ready"
    DELIVERED = "delivered"

    _TRANSITIONS: dict[OrderStatus, set[OrderStatus]]

    def can_transition_to(self, other: OrderStatus) -> bool:
        return other in _TRANSITIONS.get(self, set())

    def transition_to(self, other: OrderStatus) -> OrderStatus:
        if not self.can_transition_to(other):
            raise InvalidStateTransitionError(f"Cannot transition from {self.name} to {other.name}")
        return other


_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING_PAYMENT: {OrderStatus.PAID},
    OrderStatus.PAID: {OrderStatus.QUEUED},
    OrderStatus.QUEUED: {OrderStatus.BAKING},
    OrderStatus.BAKING: {OrderStatus.READY},
    OrderStatus.READY: {OrderStatus.DELIVERED},
}
