from enum import Enum

from src.domain.value_objects.priority import Priority


class CustomerType(Enum):
    VIP = "vip"
    APP = "app"
    WALKIN = "walkin"

    def to_priority(self) -> Priority:
        return Priority[self.name]
