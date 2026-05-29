from decimal import Decimal

import pytest
from src.domain.entities.item import Item
from src.domain.entities.order import Order
from src.domain.exceptions import DomainError, InvalidStateTransitionError
from src.domain.value_objects.bake_time import BakeTime, Category
from src.domain.value_objects.ids import (
    new_customer_id,
    new_item_id,
    new_menu_item_id,
    new_order_id,
)
from src.domain.value_objects.money import Money
from src.domain.value_objects.order_status import OrderStatus
from src.domain.value_objects.priority import Priority


def _make_item(price: str = "3.00", category: Category = Category.COOKIES) -> Item:
    return Item(
        id=new_item_id(),
        order_id=new_order_id(),
        menu_item_id=new_menu_item_id(),
        name="Cookie",
        price=Money(Decimal(price)),
        category=category,
        bake_time=BakeTime.from_category(category),
    )


def _make_order(items: list[Item] | None = None) -> Order:
    return Order(
        id=new_order_id(),
        customer_id=new_customer_id(),
        priority=Priority.APP,
        items=items if items is not None else [_make_item()],
    )


# --- Construction ---


def test_order_is_constructed_with_correct_fields() -> None:
    oid = new_order_id()
    cid = new_customer_id()
    items = [_make_item()]
    order = Order(id=oid, customer_id=cid, priority=Priority.VIP, items=items)

    assert order.id == oid
    assert order.customer_id == cid
    assert order.priority is Priority.VIP
    assert len(order.items) == 1


def test_order_initial_status_is_pending_payment() -> None:
    order = _make_order()
    assert order.status is OrderStatus.PENDING_PAYMENT


def test_order_with_no_items_raises_domain_error() -> None:
    with pytest.raises(DomainError):
        _make_order(items=[])


def test_order_items_list_is_a_defensive_copy() -> None:
    source = [_make_item()]
    order = _make_order(items=source)
    source.append(_make_item())
    assert len(order.items) == 1


# --- Total price ---


def test_total_price_is_sum_of_item_prices() -> None:
    items = [_make_item("2.50"), _make_item("4.00"), _make_item("1.50")]
    order = _make_order(items=items)
    assert order.total_price == Money(Decimal("8.00"))


def test_total_price_with_single_item() -> None:
    order = _make_order(items=[_make_item("5.99")])
    assert order.total_price == Money(Decimal("5.99"))


# --- State machine: happy path ---


def test_mark_paid_transitions_to_paid() -> None:
    order = _make_order()
    order.mark_paid()
    assert order.status is OrderStatus.PAID


def test_mark_queued_transitions_to_queued() -> None:
    order = _make_order()
    order.mark_paid()
    order.mark_queued()
    assert order.status is OrderStatus.QUEUED


def test_mark_baking_transitions_to_baking() -> None:
    order = _make_order()
    order.mark_paid()
    order.mark_queued()
    order.mark_baking()
    assert order.status is OrderStatus.BAKING


def test_mark_ready_transitions_to_ready_when_all_items_done() -> None:
    item = _make_item()
    order = _make_order(items=[item])
    order.mark_paid()
    order.mark_queued()
    order.mark_baking()
    item.start_baking()
    item.finish_baking()
    order.mark_ready()
    assert order.status is OrderStatus.READY


def test_mark_delivered_transitions_to_delivered() -> None:
    item = _make_item()
    order = _make_order(items=[item])
    order.mark_paid()
    order.mark_queued()
    order.mark_baking()
    item.start_baking()
    item.finish_baking()
    order.mark_ready()
    order.mark_delivered()
    assert order.status is OrderStatus.DELIVERED


# --- State machine: invalid transitions ---


def test_mark_queued_before_paid_raises_invalid_transition() -> None:
    order = _make_order()
    with pytest.raises(InvalidStateTransitionError):
        order.mark_queued()


def test_mark_paid_twice_raises_invalid_transition() -> None:
    order = _make_order()
    order.mark_paid()
    with pytest.raises(InvalidStateTransitionError):
        order.mark_paid()


def test_mark_ready_raises_domain_error_when_items_not_done() -> None:
    item = _make_item()
    order = _make_order(items=[item])
    order.mark_paid()
    order.mark_queued()
    order.mark_baking()
    # item still WAITING — not done
    with pytest.raises(DomainError):
        order.mark_ready()


def test_mark_ready_raises_when_only_some_items_done() -> None:
    item_a = _make_item()
    item_b = _make_item()
    order = _make_order(items=[item_a, item_b])
    order.mark_paid()
    order.mark_queued()
    order.mark_baking()
    item_a.start_baking()
    item_a.finish_baking()
    # item_b still WAITING
    with pytest.raises(DomainError):
        order.mark_ready()


# --- all_items_done ---


def test_all_items_done_is_false_initially() -> None:
    order = _make_order()
    assert order.all_items_done is False


def test_all_items_done_is_true_when_every_item_is_done() -> None:
    item_a = _make_item()
    item_b = _make_item()
    order = _make_order(items=[item_a, item_b])
    item_a.start_baking()
    item_a.finish_baking()
    item_b.start_baking()
    item_b.finish_baking()
    assert order.all_items_done is True


def test_all_items_done_is_false_when_one_item_remains() -> None:
    item_a = _make_item()
    item_b = _make_item()
    order = _make_order(items=[item_a, item_b])
    item_a.start_baking()
    item_a.finish_baking()
    assert order.all_items_done is False


# --- Identity ---


def test_equality_is_based_on_id() -> None:
    oid = new_order_id()
    a = Order(id=oid, customer_id=new_customer_id(), priority=Priority.VIP, items=[_make_item()])
    b = Order(id=oid, customer_id=new_customer_id(), priority=Priority.WALKIN, items=[_make_item()])
    assert a == b


def test_different_ids_are_not_equal() -> None:
    assert _make_order() != _make_order()


def test_order_is_hashable_by_id() -> None:
    order = _make_order()
    assert hash(order) == hash(order.id)
