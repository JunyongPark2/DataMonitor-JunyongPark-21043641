import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

from datamonitor.monitor import DataMonitor
from datamonitor.render import render_dashboard
from datamonitor.repository import OrderRepository, SampleRepository

CLEAR_SCREEN = "\033[2J\033[H"

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def run(
    monitor,
    interval=2.0,
    iterations=None,
    clock_now=datetime.now,
    sleep=time.sleep,
    out=None,
    clear=True,
):
    """실시간 모니터링 루프.

    iterations가 주어지면 해당 횟수만큼만 갱신하고 종료한다(테스트/일회성 조회용).
    None이면 Ctrl+C로 중단할 때까지 계속 갱신한다.
    """
    out = sys.stdout if out is None else out
    count = 0
    try:
        while iterations is None or count < iterations:
            timestamp = clock_now().strftime("%Y-%m-%d %H:%M:%S")
            snapshot = monitor.snapshot()
            output = render_dashboard(snapshot, timestamp)
            if clear:
                out.write(CLEAR_SCREEN)
            out.write(output + "\n")
            out.flush()
            count += 1
            if iterations is None or count < iterations:
                sleep(interval)
    except KeyboardInterrupt:
        out.write("\n모니터링을 종료합니다.\n")
    return count


def build_monitor(data_dir=DEFAULT_DATA_DIR):
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    sample_repo = SampleRepository(data_dir / "samples.json")
    order_repo = OrderRepository(data_dir / "orders.json")
    return DataMonitor(sample_repo, order_repo)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="반도체 시료 생산주문관리 시스템 - 데이터 모니터링 Tool"
    )
    parser.add_argument(
        "--data-dir",
        default=str(DEFAULT_DATA_DIR),
        help="samples.json / orders.json 이 위치한 디렉터리",
    )
    parser.add_argument(
        "--interval", type=float, default=2.0, help="갱신 주기(초), 기본 2초"
    )
    parser.add_argument(
        "--once", action="store_true", help="한 번만 조회하고 종료(스냅샷 모드)"
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    monitor = build_monitor(args.data_dir)
    run(
        monitor,
        interval=args.interval,
        iterations=1 if args.once else None,
        clear=not args.once,
    )


if __name__ == "__main__":
    main()
