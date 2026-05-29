from __future__ import annotations

from enum import Enum

from src.domain.exceptions import InvalidStateTransitionError


class ItemStatus(Enum):
    WAITING = "waiting"
    BAKING = "baking"
    DONE = "done"

    def can_transition_to(self, other: ItemStatus) -> bool:
        return other in _TRANSITIONS.get(self, set())

    def transition_to(self, other: ItemStatus) -> ItemStatus:
        if not self.can_transition_to(other):
            raise InvalidStateTransitionError(f"Cannot transition from {self.name} to {other.name}")
        return other


_TRANSITIONS: dict[ItemStatus, set[ItemStatus]] = {
    ItemStatus.WAITING: {ItemStatus.BAKING},
    ItemStatus.BAKING: {ItemStatus.DONE},
}
