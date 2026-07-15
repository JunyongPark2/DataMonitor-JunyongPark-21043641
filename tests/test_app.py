import json

from datamonitor.app import build_monitor, main, run


def test_run_stops_after_requested_iterations(monitor):
    sleep_calls = []

    count = run(
        monitor,
        interval=5,
        iterations=3,
        clock_now=lambda: _FixedNow(),
        sleep=lambda seconds: sleep_calls.append(seconds),
        out=_NullWriter(),
        clear=False,
    )

    assert count == 3
    assert sleep_calls == [5, 5]  # 마지막 반복 후에는 sleep 하지 않는다


def test_run_handles_keyboard_interrupt(monitor):
    def raising_sleep(_seconds):
        raise KeyboardInterrupt

    writer = _NullWriter()
    count = run(
        monitor,
        iterations=None,
        clock_now=lambda: _FixedNow(),
        sleep=raising_sleep,
        out=writer,
        clear=False,
    )

    assert count == 1
    assert "종료" in writer.text


def test_build_monitor_reads_seeded_data(tmp_path):
    samples = [
        {
            "sample_id": "S-001",
            "name": "실리콘 웨이퍼-8인치",
            "avg_production_time": 0.5,
            "yield_rate": 0.92,
            "stock": 100,
        }
    ]
    (tmp_path / "samples.json").write_text(json.dumps(samples), encoding="utf-8")
    (tmp_path / "orders.json").write_text("[]", encoding="utf-8")

    monitor = build_monitor(tmp_path)
    snapshot = monitor.snapshot()

    assert snapshot["sample_count"] == 1
    assert snapshot["total_stock"] == 100


def test_main_once_prints_snapshot(tmp_path, capsys, monkeypatch):
    samples = [
        {
            "sample_id": "S-001",
            "name": "실리콘 웨이퍼-8인치",
            "avg_production_time": 0.5,
            "yield_rate": 0.92,
            "stock": 100,
        }
    ]
    (tmp_path / "samples.json").write_text(json.dumps(samples), encoding="utf-8")
    (tmp_path / "orders.json").write_text("[]", encoding="utf-8")

    main(["--data-dir", str(tmp_path), "--once"])

    captured = capsys.readouterr()
    assert "실리콘 웨이퍼-8인치" in captured.out


class _FixedNow:
    def strftime(self, _fmt):
        return "2026-04-16 09:32:15"


class _NullWriter:
    def __init__(self):
        self.text = ""

    def write(self, text):
        self.text += text

    def flush(self):
        pass
