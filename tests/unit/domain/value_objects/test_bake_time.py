import pytest
from src.domain.value_objects.bake_time import BakeTime, Category


def test_bake_time_for_cookies_is_five_minutes() -> None:
    assert BakeTime.from_category(Category.COOKIES).minutes == 5


def test_bake_time_for_pastries_is_ten_minutes() -> None:
    assert BakeTime.from_category(Category.PASTRIES).minutes == 10


def test_bake_time_for_breads_is_twenty_minutes() -> None:
    assert BakeTime.from_category(Category.BREADS).minutes == 20


def test_bake_time_must_be_positive() -> None:
    with pytest.raises(ValueError):
        BakeTime(minutes=0)


def test_bake_time_for_unknown_category_raises() -> None:
    with pytest.raises(KeyError):
        BakeTime.from_category("unknown")  # type: ignore[arg-type]
