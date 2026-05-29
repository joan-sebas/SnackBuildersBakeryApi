from decimal import Decimal

import pytest
from src.domain.entities.item import Item
from src.domain.exceptions import InvalidStateTransitionError
from src.domain.value_objects.bake_time import BakeTime, Category
from src.domain.value_objects.ids import new_item_id, new_menu_item_id, new_order_id
from src.domain.value_objects.item_status import ItemStatus
from src.domain.value_objects.money import Money


def _make_item() -> Item:
    return Item(
        id=new_item_id(),
        order_id=new_order_id(),
        menu_item_id=new_menu_item_id(),
        name="Croissant",
        price=Money(Decimal("3.50")),
        category=Category.PASTRIES,
        bake_time=BakeTime.from_category(Category.PASTRIES),
    )


# --- Construction ---


def test_item_is_constructed_with_correct_fields() -> None:
    iid = new_item_id()
    oid = new_order_id()
    mid = new_menu_item_id()
    price = Money(Decimal("2.00"))
    bake_time = BakeTime.from_category(Category.COOKIES)

    item = Item(
        id=iid,
        order_id=oid,
        menu_item_id=mid,
        name="Cookie",
        price=price,
        category=Category.COOKIES,
        bake_time=bake_time,
    )

    assert item.id == iid
    assert item.order_id == oid
    assert item.menu_item_id == mid
    assert item.name == "Cookie"
    assert item.price == price
    assert item.category is Category.COOKIES
    assert item.bake_time == bake_time


def test_item_initial_status_is_waiting() -> None:
    item = _make_item()
    assert item.status is ItemStatus.WAITING


# --- State machine: happy path ---


def test_start_baking_transitions_from_waiting_to_baking() -> None:
    item = _make_item()
    item.start_baking()
    assert item.status is ItemStatus.BAKING


def test_finish_baking_transitions_from_baking_to_done() -> None:
    item = _make_item()
    item.start_baking()
    item.finish_baking()
    assert item.status is ItemStatus.DONE


def test_is_done_returns_true_only_after_finish_baking() -> None:
    item = _make_item()
    assert item.is_done is False
    item.start_baking()
    assert item.is_done is False
    item.finish_baking()
    assert item.is_done is True


# --- State machine: invalid transitions ---


def test_start_baking_twice_raises_invalid_transition() -> None:
    item = _make_item()
    item.start_baking()
    with pytest.raises(InvalidStateTransitionError):
        item.start_baking()


def test_finish_baking_without_start_raises_invalid_transition() -> None:
    item = _make_item()
    with pytest.raises(InvalidStateTransitionError):
        item.finish_baking()


def test_finish_baking_twice_raises_invalid_transition() -> None:
    item = _make_item()
    item.start_baking()
    item.finish_baking()
    with pytest.raises(InvalidStateTransitionError):
        item.finish_baking()


def test_start_baking_after_done_raises_invalid_transition() -> None:
    item = _make_item()
    item.start_baking()
    item.finish_baking()
    with pytest.raises(InvalidStateTransitionError):
        item.start_baking()


# --- Immutability once BAKING ---


def test_baking_item_status_cannot_revert_to_waiting() -> None:
    item = _make_item()
    item.start_baking()
    # The state machine enforces this; direct attribute assignment is bypassed by the property
    with pytest.raises(InvalidStateTransitionError):
        item.start_baking()  # would be BAKING -> BAKING, which is invalid
    assert item.status is ItemStatus.BAKING


# --- Identity ---


def test_equality_is_based_on_id() -> None:
    iid = new_item_id()
    a = Item(
        id=iid,
        order_id=new_order_id(),
        menu_item_id=new_menu_item_id(),
        name="A",
        price=Money(Decimal("1.00")),
        category=Category.COOKIES,
        bake_time=BakeTime.from_category(Category.COOKIES),
    )
    b = Item(
        id=iid,
        order_id=new_order_id(),
        menu_item_id=new_menu_item_id(),
        name="B",
        price=Money(Decimal("9.00")),
        category=Category.BREADS,
        bake_time=BakeTime.from_category(Category.BREADS),
    )
    assert a == b


def test_different_ids_are_not_equal() -> None:
    a = _make_item()
    b = _make_item()
    assert a != b


def test_item_is_hashable_by_id() -> None:
    item = _make_item()
    assert hash(item) == hash(item.id)
