import pytest

from datamonitor.models import Order, OrderStatus, Sample
from datamonitor.repository import OrderRepository, SampleRepository

CREATED_AT = "2026-07-15T00:00:00+00:00"


def test_add_and_get_sample(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")
    repo.add(Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, stock=100))

    found = repo.get("S-001")
    assert found.name == "실리콘 웨이퍼-8인치"
    assert found.stock == 100


def test_get_missing_sample_returns_none(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")
    assert repo.get("NOPE") is None


def test_data_persists_across_repository_instances(tmp_path):
    path = tmp_path / "samples.json"
    SampleRepository(path).add(Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, stock=100))

    reloaded = SampleRepository(path)
    assert reloaded.get("S-001").stock == 100


def test_update_sample_stock(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")
    repo.add(Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, stock=100))

    repo.update("S-001", stock=50)

    assert repo.get("S-001").stock == 50


def test_update_missing_sample_raises(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")
    with pytest.raises(KeyError):
        repo.update("NOPE", stock=1)


def test_delete_sample(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")
    repo.add(Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, stock=100))

    repo.delete("S-001")

    assert repo.get("S-001") is None


def test_order_repository_crud(tmp_path):
    repo = OrderRepository(tmp_path / "orders.json")
    repo.add(Order("ORD-0001", "S-001", "SK하이닉스", 150, OrderStatus.RESERVED, CREATED_AT))

    repo.update("ORD-0001", status=OrderStatus.CONFIRMED)
    order = repo.get("ORD-0001")

    assert order.status == OrderStatus.CONFIRMED
    assert order.customer_name == "SK하이닉스"
    assert len(repo.list_all()) == 1


def test_mtime_changes_after_write(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")
    before = repo.mtime()

    repo.add(Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, stock=100))

    assert repo.mtime() >= before
