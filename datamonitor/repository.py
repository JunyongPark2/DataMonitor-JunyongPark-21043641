import json
from pathlib import Path

from datamonitor.models import Order, Sample


class JsonFileRepository:
    """JSON 파일에 데이터를 영속화하는 공용 저장소.

    파일의 mtime을 함께 노출해 DataMonitor가 외부에서 변경된 데이터를
    다시 읽어야 하는 시점을 판단할 수 있도록 한다.
    """

    def __init__(self, path, record_cls):
        self._path = Path(path)
        self._record_cls = record_cls
        if not self._path.exists():
            self._write([])

    @property
    def path(self):
        return self._path

    def mtime(self):
        return self._path.stat().st_mtime

    def _read(self):
        raw = json.loads(self._path.read_text(encoding="utf-8") or "[]")
        return [self._record_cls.from_dict(item) for item in raw]

    def _write(self, records):
        payload = [r.to_dict() if hasattr(r, "to_dict") else r for r in records]
        self._path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def list_all(self):
        return self._read()

    def get(self, record_id, id_field):
        for record in self._read():
            if getattr(record, id_field) == record_id:
                return record
        return None

    def add(self, record):
        records = self._read()
        records.append(record)
        self._write(records)
        return record

    def update(self, record_id, id_field, **changes):
        records = self._read()
        updated = None
        for record in records:
            if getattr(record, id_field) == record_id:
                for key, value in changes.items():
                    setattr(record, key, value)
                updated = record
                break
        if updated is None:
            raise KeyError(f"{id_field}={record_id} not found")
        self._write(records)
        return updated

    def delete(self, record_id, id_field):
        records = self._read()
        remaining = [r for r in records if getattr(r, id_field) != record_id]
        if len(remaining) == len(records):
            raise KeyError(f"{id_field}={record_id} not found")
        self._write(remaining)


class SampleRepository(JsonFileRepository):
    def __init__(self, path):
        super().__init__(path, Sample)

    def get(self, sample_id):
        return super().get(sample_id, "sample_id")

    def update(self, sample_id, **changes):
        return super().update(sample_id, "sample_id", **changes)

    def delete(self, sample_id):
        return super().delete(sample_id, "sample_id")


class OrderRepository(JsonFileRepository):
    def __init__(self, path):
        super().__init__(path, Order)

    def get(self, order_id):
        return super().get(order_id, "order_id")

    def update(self, order_id, **changes):
        return super().update(order_id, "order_id", **changes)

    def delete(self, order_id):
        return super().delete(order_id, "order_id")
