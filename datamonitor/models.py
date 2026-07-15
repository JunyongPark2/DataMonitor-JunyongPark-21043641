from dataclasses import dataclass
from enum import Enum


class OrderStatus(Enum):
    RESERVED = "RESERVED"
    REJECTED = "REJECTED"
    PRODUCING = "PRODUCING"
    CONFIRMED = "CONFIRMED"
    RELEASE = "RELEASE"


# REJECTED는 정상 흐름 외의 상태이므로 모니터링 대상에서 제외한다.
MONITORED_STATUSES = (
    OrderStatus.RESERVED,
    OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED,
    OrderStatus.RELEASE,
)


@dataclass
class Sample:
    sample_id: str
    name: str
    avg_production_time: float
    yield_rate: float
    stock: int

    def to_dict(self) -> dict:
        return {
            "sample_id": self.sample_id,
            "name": self.name,
            "avg_production_time": self.avg_production_time,
            "yield_rate": self.yield_rate,
            "stock": self.stock,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Sample":
        return cls(
            sample_id=data["sample_id"],
            name=data["name"],
            avg_production_time=data["avg_production_time"],
            yield_rate=data["yield_rate"],
            stock=data["stock"],
        )


@dataclass
class Order:
    order_id: str
    sample_id: str
    customer_name: str
    quantity: int
    status: OrderStatus
    created_at: str

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "sample_id": self.sample_id,
            "customer_name": self.customer_name,
            "quantity": self.quantity,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        return cls(
            order_id=data["order_id"],
            sample_id=data["sample_id"],
            customer_name=data["customer_name"],
            quantity=data["quantity"],
            status=OrderStatus(data["status"]),
            created_at=data["created_at"],
        )
