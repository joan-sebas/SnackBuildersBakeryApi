import pytest
from src.domain.exceptions import InvalidStateTransitionError
from src.domain.value_objects.order_status import OrderStatus


def test_order_status_pending_payment_to_paid_is_valid() -> None:
    assert OrderStatus.PENDING_PAYMENT.transition_to(OrderStatus.PAID) is OrderStatus.PAID


def test_order_status_paid_to_queued_is_valid() -> None:
    assert OrderStatus.PAID.transition_to(OrderStatus.QUEUED) is OrderStatus.QUEUED


def test_order_status_queued_to_baking_is_valid() -> None:
    assert OrderStatus.QUEUED.transition_to(OrderStatus.BAKING) is OrderStatus.BAKING


def test_order_status_baking_to_ready_is_valid() -> None:
    assert OrderStatus.BAKING.transition_to(OrderStatus.READY) is OrderStatus.READY


def test_order_status_ready_to_delivered_is_valid() -> None:
    assert OrderStatus.READY.transition_to(OrderStatus.DELIVERED) is OrderStatus.DELIVERED


def test_order_status_skipping_state_raises() -> None:
    with pytest.raises(InvalidStateTransitionError):
        OrderStatus.PENDING_PAYMENT.transition_to(OrderStatus.QUEUED)


def test_order_status_backwards_transition_raises() -> None:
    with pytest.raises(InvalidStateTransitionError):
        OrderStatus.BAKING.transition_to(OrderStatus.PAID)
