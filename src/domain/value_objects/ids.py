"""Typed identifiers for domain entities, backed by UUID."""

from typing import NewType
from uuid import UUID, uuid4

OrderId = NewType("OrderId", UUID)
ItemId = NewType("ItemId", UUID)
CustomerId = NewType("CustomerId", UUID)
MenuItemId = NewType("MenuItemId", UUID)
OvenId = NewType("OvenId", UUID)
SlotId = NewType("SlotId", UUID)


def new_order_id() -> OrderId:
    return OrderId(uuid4())


def new_item_id() -> ItemId:
    return ItemId(uuid4())


def new_customer_id() -> CustomerId:
    return CustomerId(uuid4())


def new_menu_item_id() -> MenuItemId:
    return MenuItemId(uuid4())


def new_oven_id() -> OvenId:
    return OvenId(uuid4())


def new_slot_id() -> SlotId:
    return SlotId(uuid4())
