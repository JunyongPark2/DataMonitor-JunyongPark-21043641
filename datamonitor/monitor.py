from datamonitor.models import MONITORED_STATUSES, OrderStatus

STOCK_DEPLETED = "고갈"
STOCK_SHORTAGE = "부족"
STOCK_SUFFICIENT = "여유"

# 고갈/부족 여부 판단에 사용하는, 아직 출고되지 않은(=재고를 필요로 하는) 상태들.
PENDING_DEMAND_STATUSES = (
    OrderStatus.RESERVED,
    OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED,
)


class DataMonitor:
    """시료 저장소와 주문 저장소를 조회해 현재 데이터 상태를 집계한다."""

    def __init__(self, sample_repo, order_repo):
        self._sample_repo = sample_repo
        self._order_repo = order_repo

    def order_status_counts(self):
        counts = {status.value: 0 for status in MONITORED_STATUSES}
        for order in self._order_repo.list_all():
            if order.status in MONITORED_STATUSES:
                counts[OrderStatus(order.status).value] += 1
        return counts

    def pending_demand_by_sample(self):
        demand = {}
        for order in self._order_repo.list_all():
            if order.status in PENDING_DEMAND_STATUSES:
                demand[order.sample_id] = demand.get(order.sample_id, 0) + order.quantity
        return demand

    def stock_status(self, sample, pending_demand=0):
        if sample.stock <= 0:
            return STOCK_DEPLETED
        if sample.stock < pending_demand:
            return STOCK_SHORTAGE
        return STOCK_SUFFICIENT

    def stock_report(self):
        demand_by_sample = self.pending_demand_by_sample()
        report = []
        for sample in self._sample_repo.list_all():
            demand = demand_by_sample.get(sample.sample_id, 0)
            percentage = self._remaining_ratio(sample.stock, demand)
            report.append(
                {
                    "sample_id": sample.sample_id,
                    "name": sample.name,
                    "stock": sample.stock,
                    "status": self.stock_status(sample, demand),
                    "percentage": round(percentage, 1),
                }
            )
        return report

    @staticmethod
    def _remaining_ratio(stock, pending_demand):
        """대기 수요를 채우고 남는 재고의 비율. 수요가 재고보다 많으면(음수) 0%로 클램프한다."""
        if stock <= 0:
            return 0.0
        if pending_demand <= 0:
            return 100.0
        ratio = (stock - pending_demand) / stock * 100
        return round(max(0.0, min(100.0, ratio)), 1)

    def snapshot(self):
        samples = self._sample_repo.list_all()
        orders = self._order_repo.list_all()
        monitored_orders = [o for o in orders if o.status in MONITORED_STATUSES]
        return {
            "sample_count": len(samples),
            "total_stock": sum(s.stock for s in samples),
            "total_orders": len(monitored_orders),
            "order_status_counts": self.order_status_counts(),
            "stock_report": self.stock_report(),
        }
