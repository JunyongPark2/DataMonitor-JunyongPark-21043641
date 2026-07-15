WIDTH = 64
BAR_WIDTH = 20


def _rule(char="-"):
    return char * WIDTH


def _bar(percentage):
    filled = round(BAR_WIDTH * percentage / 100)
    return "#" * filled + "-" * (BAR_WIDTH - filled)


def render_dashboard(snapshot, timestamp):
    lines = []
    lines.append(_rule("="))
    lines.append(f" [4] 데이터 모니터링 Tool          {timestamp}")
    lines.append(_rule("="))
    lines.append(
        f" 등록 시료  {snapshot['sample_count']:>3}종"
        f"      총 재고   {snapshot['total_stock']:>6,} ea"
    )
    lines.append(f" 전체 주문  {snapshot['total_orders']:>3}건")
    lines.append(_rule())

    lines.append(" 상태별 주문 현황")
    for status, count in snapshot["order_status_counts"].items():
        suffix = "  <- 생산라인 대기" if status == "PRODUCING" and count else ""
        lines.append(f"   {status:<10} {count:>3}건{suffix}")
    lines.append(_rule())

    lines.append(" 재고 현황")
    lines.append(f" {'시료명':<20}{'재고':>10}   {'상태':<4} 잔여율")
    for row in snapshot["stock_report"]:
        lines.append(
            f" {row['name']:<20}{row['stock']:>7,} ea   {row['status']:<4}"
            f" [{_bar(row['percentage'])}] {row['percentage']:>5.1f}%"
        )
    lines.append(_rule())
    lines.append(" (Ctrl+C 로 종료)")
    return "\n".join(lines)
