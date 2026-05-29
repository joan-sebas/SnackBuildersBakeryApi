from decimal import Decimal

import pytest
from src.domain.entities.menu_item import MenuItem
from src.domain.value_objects.bake_time import Category
from src.domain.value_objects.ids import new_menu_item_id
from src.domain.value_objects.money import Money


def _make_item(*, available: bool = True) -> MenuItem:
    return MenuItem(
        id=new_menu_item_id(),
        name="Croissant",
        price=Money(Decimal("3.50")),
        category=Category.PASTRIES,
        available=available,
    )


def test_menu_item_is_constructed_with_correct_fields() -> None:
    mid = new_menu_item_id()
    price = Money(Decimal("2.00"))
    item = MenuItem(id=mid, name="Cookie", price=price, category=Category.COOKIES)

    assert item.id == mid
    assert item.name == "Cookie"
    assert item.price == price
    assert item.category is Category.COOKIES
    assert item.available is True


def test_menu_item_available_defaults_to_true() -> None:
    item = _make_item()
    assert item.available is True


def test_menu_item_can_be_constructed_as_unavailable() -> None:
    item = _make_item(available=False)
    assert item.available is False


def test_disable_makes_item_unavailable() -> None:
    item = _make_item(available=True)
    item.disable()
    assert item.available is False


def test_enable_makes_item_available() -> None:
    item = _make_item(available=False)
    item.enable()
    assert item.available is True


def test_toggle_availability_is_idempotent_when_repeated() -> None:
    item = _make_item(available=True)
    item.disable()
    item.disable()
    assert item.available is False

    item.enable()
    item.enable()
    assert item.available is True


@pytest.mark.parametrize(
    "category",
    [Category.COOKIES, Category.PASTRIES, Category.BREADS],
)
def test_category_is_preserved_for_all_types(category: Category) -> None:
    item = MenuItem(
        id=new_menu_item_id(),
        name="Item",
        price=Money(Decimal("1.00")),
        category=category,
    )
    assert item.category is category


def test_equality_is_based_on_id() -> None:
    mid = new_menu_item_id()
    price = Money(Decimal("5.00"))
    a = MenuItem(id=mid, name="A", price=price, category=Category.BREADS)
    b = MenuItem(id=mid, name="B", price=price, category=Category.COOKIES)
    assert a == b


def test_different_ids_are_not_equal() -> None:
    price = Money(Decimal("5.00"))
    a = MenuItem(id=new_menu_item_id(), name="A", price=price, category=Category.BREADS)
    b = MenuItem(id=new_menu_item_id(), name="A", price=price, category=Category.BREADS)
    assert a != b


def test_menu_item_is_hashable_by_id() -> None:
    item = _make_item()
    assert hash(item) == hash(item.id)
