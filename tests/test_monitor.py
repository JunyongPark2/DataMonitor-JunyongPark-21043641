from datamonitor.models import Order, OrderStatus, Sample
from datamonitor.monitor import DataMonitor, STOCK_DEPLETED, STOCK_SHORTAGE, STOCK_SUFFICIENT

CREATED_AT = "2026-07-15T00:00:00+00:00"


def test_order_status_counts_excludes_rejected(monitor):
    counts = monitor.order_status_counts()

    assert counts == {
        "RESERVED": 1,
        "PRODUCING": 1,
        "CONFIRMED": 1,
        "RELEASE": 0,
    }
    assert "REJECTED" not in counts


def test_pending_demand_ignores_release_and_rejected(sample_repo, order_repo):
    order_repo.add(Order("ORD-0005", "S-001", "고객A", 999, OrderStatus.RELEASE, CREATED_AT))
    monitor = DataMonitor(sample_repo, order_repo)

    demand = monitor.pending_demand_by_sample()

    assert demand["S-001"] == 150
    assert "S-999" not in demand  # REJECTED 주문의 시료는 제외


def test_stock_status_depleted_when_zero():
    monitor = DataMonitor(None, None)
    sample = Sample("S-005", "산화막 웨이퍼-SiO2", 0.6, 0.88, stock=0)

    assert monitor.stock_status(sample, pending_demand=10) == STOCK_DEPLETED


def test_stock_status_depleted_when_negative():
    monitor = DataMonitor(None, None)
    sample = Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, stock=-520)

    assert monitor.stock_status(sample, pending_demand=0) == STOCK_DEPLETED


def test_stock_status_shortage_when_demand_exceeds_stock():
    monitor = DataMonitor(None, None)
    sample = Sample("S-003", "SiC 파워기판-6인치", 0.8, 0.92, stock=30)

    assert monitor.stock_status(sample, pending_demand=200) == STOCK_SHORTAGE


def test_stock_status_sufficient_when_demand_within_stock():
    monitor = DataMonitor(None, None)
    sample = Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, stock=480)

    assert monitor.stock_status(sample, pending_demand=150) == STOCK_SUFFICIENT


def test_stock_report_matches_expected_statuses(monitor):
    report = {row["sample_id"]: row for row in monitor.stock_report()}

    assert report["S-001"]["status"] == STOCK_SUFFICIENT
    assert report["S-003"]["status"] == STOCK_SHORTAGE
    assert report["S-005"]["status"] == STOCK_DEPLETED
    assert report["S-005"]["percentage"] == 0.0


def test_remaining_ratio_full_when_no_demand():
    assert DataMonitor._remaining_ratio(100, 0) == 100.0


def test_remaining_ratio_clamped_to_zero_when_demand_exceeds_stock():
    # stock=30, demand=200 -> (30-200)/30 is negative, clamp to 0
    assert DataMonitor._remaining_ratio(30, 200) == 0.0


def test_remaining_ratio_reflects_surplus_left_after_demand():
    # stock=480, demand=150 -> (480-150)/480 * 100
    assert DataMonitor._remaining_ratio(480, 150) == 68.8


def test_snapshot_aggregates_totals(monitor):
    snapshot = monitor.snapshot()

    assert snapshot["sample_count"] == 3
    assert snapshot["total_stock"] == 480 + 30 + 0
    assert snapshot["total_orders"] == 3  # REJECTED 1건 제외
    assert len(snapshot["stock_report"]) == 3
