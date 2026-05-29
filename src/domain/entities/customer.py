from src.domain.value_objects.customer_type import CustomerType
from src.domain.value_objects.ids import CustomerId
from src.domain.value_objects.priority import Priority


class Customer:
    """A customer whose scheduling priority is derived from their type."""

    def __init__(self, id: CustomerId, name: str, customer_type: CustomerType) -> None:
        self.id = id
        self.name = name
        self.customer_type = customer_type

    @property
    def priority(self) -> Priority:
        return self.customer_type.to_priority()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Customer):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
