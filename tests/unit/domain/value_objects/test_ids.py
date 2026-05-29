from uuid import UUID

from src.domain.value_objects.ids import (
    new_customer_id,
    new_item_id,
    new_menu_item_id,
    new_order_id,
    new_oven_id,
    new_slot_id,
)


def test_new_order_id_returns_uuid() -> None:
    assert isinstance(new_order_id(), UUID)


def test_new_item_id_returns_uuid() -> None:
    assert isinstance(new_item_id(), UUID)


def test_new_customer_id_returns_uuid() -> None:
    assert isinstance(new_customer_id(), UUID)


def test_new_menu_item_id_returns_uuid() -> None:
    assert isinstance(new_menu_item_id(), UUID)


def test_new_oven_id_returns_uuid() -> None:
    assert isinstance(new_oven_id(), UUID)


def test_new_slot_id_returns_uuid() -> None:
    assert isinstance(new_slot_id(), UUID)


def test_each_call_produces_unique_id() -> None:
    assert new_order_id() != new_order_id()
