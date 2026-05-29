import pytest
from src.domain.exceptions import InvalidStateTransitionError
from src.domain.value_objects.item_status import ItemStatus


def test_item_status_waiting_to_baking_is_valid() -> None:
    assert ItemStatus.WAITING.transition_to(ItemStatus.BAKING) is ItemStatus.BAKING


def test_item_status_baking_to_done_is_valid() -> None:
    assert ItemStatus.BAKING.transition_to(ItemStatus.DONE) is ItemStatus.DONE


def test_item_status_skipping_done_raises() -> None:
    with pytest.raises(InvalidStateTransitionError):
        ItemStatus.WAITING.transition_to(ItemStatus.DONE)


def test_item_status_baking_to_waiting_raises() -> None:
    with pytest.raises(InvalidStateTransitionError):
        ItemStatus.BAKING.transition_to(ItemStatus.WAITING)
