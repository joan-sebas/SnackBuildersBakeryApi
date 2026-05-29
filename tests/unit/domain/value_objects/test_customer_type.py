from src.domain.value_objects.customer_type import CustomerType
from src.domain.value_objects.priority import Priority


def test_vip_customer_maps_to_vip_priority() -> None:
    assert CustomerType.VIP.to_priority() is Priority.VIP


def test_app_customer_maps_to_app_priority() -> None:
    assert CustomerType.APP.to_priority() is Priority.APP


def test_walkin_customer_maps_to_walkin_priority() -> None:
    assert CustomerType.WALKIN.to_priority() is Priority.WALKIN
