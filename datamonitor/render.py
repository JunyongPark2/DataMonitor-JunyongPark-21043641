import unicodedata

WIDTH = 64
BAR_WIDTH = 20


def _rule(char="-"):
    return char * WIDTH


def _display_width(text):
    """한글 등 전각 문자는 터미널에서 2칸을 차지하므로, len()이 아닌 실제 표시 폭을 센다."""
    return sum(2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1 for ch in text)


def _ljust(text, width):
    return text + " " * max(0, width - _display_width(text))


def _rjust(text, width):
    return " " * max(0, width - _display_width(text)) + text


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
    lines.append(f" {_ljust('시료명', 20)}{_rjust('재고', 10)}   {_ljust('상태', 4)} 잔여율")
    for row in snapshot["stock_report"]:
        lines.append(
            f" {_ljust(row['name'], 20)}{row['stock']:>7,} ea   {_ljust(row['status'], 4)}"
            f" [{_bar(row['percentage'])}] {row['percentage']:>5.1f}%"
        )
    lines.append(_rule())
    lines.append(" (Ctrl+C 로 종료)")
    return "\n".join(lines)
