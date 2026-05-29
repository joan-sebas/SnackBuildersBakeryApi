import pytest
from src.domain.entities.customer import Customer
from src.domain.value_objects.customer_type import CustomerType
from src.domain.value_objects.ids import new_customer_id
from src.domain.value_objects.priority import Priority


def test_customer_is_constructed_with_id_name_and_type() -> None:
    cid = new_customer_id()
    customer = Customer(id=cid, name="Alice", customer_type=CustomerType.VIP)
    assert customer.id == cid
    assert customer.name == "Alice"
    assert customer.customer_type is CustomerType.VIP


@pytest.mark.parametrize(
    "customer_type, expected_priority",
    [
        (CustomerType.VIP, Priority.VIP),
        (CustomerType.APP, Priority.APP),
        (CustomerType.WALKIN, Priority.WALKIN),
    ],
)
def test_customer_priority_matches_type(
    customer_type: CustomerType, expected_priority: Priority
) -> None:
    customer = Customer(id=new_customer_id(), name="Test", customer_type=customer_type)
    assert customer.priority is expected_priority


def test_walkin_customer_can_be_created_anonymous() -> None:
    customer = Customer(id=new_customer_id(), name="Walk-in", customer_type=CustomerType.WALKIN)
    assert customer.name == "Walk-in"
    assert customer.priority is Priority.WALKIN
