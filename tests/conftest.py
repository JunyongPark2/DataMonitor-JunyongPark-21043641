import pytest

from datamonitor.models import Order, OrderStatus, Sample
from datamonitor.monitor import DataMonitor
from datamonitor.repository import OrderRepository, SampleRepository

CREATED_AT = "2026-07-15T00:00:00+00:00"


@pytest.fixture
def sample_repo(tmp_path):
    repo = SampleRepository(tmp_path / "samples.json")
    repo.add(Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, stock=480))
    repo.add(Sample("S-003", "SiC 파워기판-6인치", 0.8, 0.92, stock=30))
    repo.add(Sample("S-005", "산화막 웨이퍼-SiO2", 0.6, 0.88, stock=0))
    return repo


@pytest.fixture
def order_repo(tmp_path):
    repo = OrderRepository(tmp_path / "orders.json")
    repo.add(Order("ORD-0001", "S-001", "SK하이닉스", 150, OrderStatus.CONFIRMED, CREATED_AT))
    repo.add(Order("ORD-0002", "S-003", "삼성전자", 200, OrderStatus.PRODUCING, CREATED_AT))
    repo.add(Order("ORD-0003", "S-005", "LG이노텍", 300, OrderStatus.RESERVED, CREATED_AT))
    repo.add(Order("ORD-0004", "S-999", "DB하이텍", 100, OrderStatus.REJECTED, CREATED_AT))
    return repo


@pytest.fixture
def monitor(sample_repo, order_repo):
    return DataMonitor(sample_repo, order_repo)
