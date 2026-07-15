from datamonitor.models import Order, OrderStatus, Sample


def test_sample_round_trip_dict():
    sample = Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, stock=100)
    restored = Sample.from_dict(sample.to_dict())
    assert restored == sample


def test_sample_stock_can_be_negative():
    sample = Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, stock=-520)
    assert sample.stock == -520


def test_order_round_trip_dict():
    order = Order(
        "ORD-0001", "S-001", "SK하이닉스", 150, OrderStatus.CONFIRMED, "2026-07-15T01:00:00+00:00"
    )
    restored = Order.from_dict(order.to_dict())
    assert restored == order
    assert restored.status == OrderStatus.CONFIRMED
