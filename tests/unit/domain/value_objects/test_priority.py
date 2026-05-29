import heapq

from src.domain.value_objects.priority import Priority


def test_priority_vip_orders_before_app() -> None:
    assert Priority.VIP < Priority.APP


def test_priority_app_orders_before_walkin() -> None:
    assert Priority.APP < Priority.WALKIN


def test_priority_equality_for_same_tier() -> None:
    assert Priority.VIP == Priority.VIP
    assert Priority.APP == Priority.APP
    assert Priority.WALKIN == Priority.WALKIN


def test_priority_supports_min_heap_ordering() -> None:
    heap = [Priority.WALKIN, Priority.VIP, Priority.APP]
    heapq.heapify(heap)
    assert heapq.heappop(heap) is Priority.VIP
    assert heapq.heappop(heap) is Priority.APP
    assert heapq.heappop(heap) is Priority.WALKIN
