from decimal import Decimal

import pytest
from src.domain.value_objects.money import CurrencyMismatchError, Money


def test_money_addition_returns_sum_of_amounts() -> None:
    assert Money(Decimal("2.50")) + Money(Decimal("1.25")) == Money(Decimal("3.75"))


def test_money_subtraction_returns_difference() -> None:
    assert Money(Decimal("5.00")) - Money(Decimal("1.50")) == Money(Decimal("3.50"))


def test_money_subtraction_below_zero_raises() -> None:
    with pytest.raises(ValueError):
        Money(Decimal("1.00")) - Money(Decimal("2.00"))


def test_money_multiplication_by_positive_integer_scales_amount() -> None:
    assert Money(Decimal("2.50")) * 3 == Money(Decimal("7.50"))


def test_money_equality_requires_same_amount_and_currency() -> None:
    assert Money(Decimal("1.00"), "USD") == Money(Decimal("1.00"), "USD")
    assert Money(Decimal("1.00"), "USD") != Money(Decimal("1.00"), "EUR")
    assert Money(Decimal("1.00")) != Money(Decimal("2.00"))


def test_money_creation_with_negative_amount_raises() -> None:
    with pytest.raises(ValueError):
        Money(Decimal("-1.00"))


def test_money_arithmetic_across_currencies_raises() -> None:
    with pytest.raises(CurrencyMismatchError):
        Money(Decimal("1.00"), "USD") + Money(Decimal("1.00"), "EUR")
